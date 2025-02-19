from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import time
import os
import requests
import getpass
import shutil
import hashlib

# Dictionnaire global pour stocker les hash des images téléchargées et leur nom de fichier
downloaded_images = {}

# =====================================================
# 1️⃣ Collecte des informations de connexion et cours
# =====================================================
print("=== Paramètres de connexion ===")
email = input("Entrez votre email : ")
password = getpass.getpass("Entrez votre mot de passe : ")

print("\n=== Informations sur les cours ===")
try:
    nb_liens = int(input("Combien de liens souhaitez-vous traiter ? : "))
except ValueError:
    print("Entrée invalide pour le nombre de liens.")
    exit()

# Stocker les informations de chaque cours sous forme de tuple (URL, nombre_de_slides)
cours_info = []
for i in range(nb_liens):
    url = input(f"Entrez l'URL du cours n°{i+1} : ")
    try:
        nb_slides = int(input(f"Combien de slides pour le cours n°{i+1} ? : "))
    except ValueError:
        print("Entrée invalide pour le nombre de slides, on prendra 1 slide par défaut.")
        nb_slides = 1
    cours_info.append((url, nb_slides))

# =====================================================
# 2️⃣ Configuration de Selenium et authentification
# =====================================================
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-logging")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
chrome_options.add_argument("--log-level=3")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)

login_url = "https://reussistonifsi.learnybox.com/connexion/"
driver.get(login_url)
try:
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email_input.clear()
    email_input.send_keys(email)
    password_input = driver.find_element(By.NAME, "password")
    password_input.clear()
    password_input.send_keys(password)
    password_input.submit()
    
    # Attendre que l'élément contenant le texte "Les cours de Réussis ton IFSI" soit présent
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Les cours de Réussis ton IFSI')]"))
    )
    print("✅ Connexion réussie !")
    time.sleep(2)
except Exception as e:
    print(f"❌ Erreur lors de la connexion : {e}")
    driver.quit()
    exit()

# =====================================================
# 3️⃣ Fonctions utilitaires
# =====================================================

# 🔥 Fonction pour télécharger une image en évitant les doublons
def download_image(img_url, filename):
    try:
        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            image_bytes = response.content
            # Calcul du hash MD5 de l'image
            image_hash = hashlib.md5(image_bytes).hexdigest()
            if image_hash in downloaded_images:
                print(f"✅ Image déjà téléchargée, utilisation du fichier existant : {downloaded_images[image_hash]}")
                return downloaded_images[image_hash]
            else:
                with open(filename, 'wb') as file:
                    file.write(image_bytes)
                downloaded_images[image_hash] = filename
                print(f"✅ Image enregistrée : {filename}")
                return filename
        else:
            print(f"⚠️ Erreur lors du téléchargement : {img_url}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur de connexion : {e}")

# 🔥 Fonction pour convertir les images en PDF avec PIL
def images_to_pdf(image_folder, output_pdf_path):
    # S'assurer que le nom du fichier se termine par .pdf
    if not output_pdf_path.lower().endswith('.pdf'):
        output_pdf_path += '.pdf'
    
    # Récupérer la liste des fichiers d'image
    image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'))]
    
    if not image_files:
        print("⚠️ Aucune image trouvée dans le dossier spécifié.")
        return
    
    # Trier les fichiers par nom (l'ordre est important si les images sont nommées par slide)
    image_files.sort()
    
    # Créer une liste d'objets Image en mode RGB
    images = []
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        try:
            img = Image.open(image_path).convert('RGB')
            images.append(img)
        except Exception as e:
            print(f"⚠️ Erreur lors de l'ouverture de l'image {image_file} : {e}")
    
    if images:
        images[0].save(output_pdf_path, save_all=True, append_images=images[1:])
        print(f"📄 PDF créé avec succès : {output_pdf_path}")
    else:
        print("⚠️ Aucune image valide à ajouter au PDF.")

    # Supprimer le dossier temporaire contenant les images
    shutil.rmtree(image_folder)
    print("🗑️ Images supprimées après création du PDF.")

# 🔥 Fonction pour traiter un cours
def traiter_cours(url, nombre_slides):
    print(f"\n📖 Traitement du lien : {url}")
    driver.get(url)
    time.sleep(3)
    
    # Récupérer le titre du cours
    try:
        title_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".module-page h3"))
        )
        full_title = title_element.text.strip()
        pdf_title = full_title.split("-")[0].strip() if "-" in full_title else full_title
        print(f"📚 Titre du cours : {pdf_title}")
    except Exception as e:
        print(f"⚠️ Titre introuvable : {e}")
        pdf_title = "cours_sans_titre"
    
    # Création d'un dossier temporaire pour stocker les images
    safe_title = "".join(c for c in pdf_title if c.isalnum() or c in (" ", "_", "-")).rstrip()
    temp_folder = os.path.join(os.getcwd(), f"temp_images_{safe_title.replace(' ', '_')}")
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    
    # Pour chaque slide, récupérer les images et passer à la suivante
    for i in range(nombre_slides):
        print(f"📑 Traitement de la slide {i+1}/{nombre_slides}")
        try:
            image_elements = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".slick-slide img"))
            )
            if not image_elements:
                print("⚠️ Aucune image trouvée sur cette slide.")
            else:
                for index, img in enumerate(image_elements):
                    driver.execute_script("arguments[0].scrollIntoView(true);", img)
                    # Essayer de récupérer l'URL via 'src' ou 'data-src'
                    img_url = img.get_attribute("src") or img.get_attribute("data-src")
                    if img_url:
                        filename = os.path.join(temp_folder, f"slide_{i+1}_{index+1}.png")
                        download_image(img_url, filename)
                    else:
                        print("⚠️ Aucun URL trouvée pour une image.")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des images : {e}")
        
        # Passage à la slide suivante, sauf si c'est la dernière
        if i < nombre_slides - 1:
            try:
                current_slide = driver.find_element(By.CSS_SELECTOR, ".slick-slide.slick-active img")
                current_src = current_slide.get_attribute("src")
                # Récupérer toutes les flèches et cliquer sur la deuxième (celle qui va en avant)
                next_buttons = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".btn.btn-success"))
                )
                if len(next_buttons) >= 2:
                    next_buttons[1].click()
                    print("➡️ Passage à la slide suivante...")
                    try:
                        WebDriverWait(driver, 10).until(
                            lambda d: d.find_element(By.CSS_SELECTOR, ".slick-slide.slick-active img").get_attribute("src") != current_src
                        )
                    except Exception:
                        print("⏱️ Timeout: la nouvelle slide n'a pas été détectée, on continue.")
                else:
                    print("⚠️ Deuxième flèche introuvable.")
                    break
            except Exception as e:
                print(f"⚠️ Impossible de passer à la slide suivante : {e}")
                break

    # Conversion des images téléchargées en PDF (utilise PIL)
    output_pdf = os.path.join(os.getcwd(), f"{safe_title}.pdf")
    images_to_pdf(temp_folder, output_pdf)

# =====================================================
# 4️⃣ Traitement de tous les cours
# =====================================================
for url, nb_slides in cours_info:
    traiter_cours(url, nb_slides)

driver.quit()
print("\n✅ Tous les cours ont été traités avec succès. 🎉")
