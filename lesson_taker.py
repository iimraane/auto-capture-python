from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fpdf import FPDF
from PIL import Image
import time
import os
import requests
import getpass
import shutil

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

# 🔥 Fonction pour télécharger une image
def download_image(img_url, filename):
    try:
        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"✅ Image enregistrée : {filename}")
        else:
            print(f"⚠️ Erreur lors du téléchargement : {img_url}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur de connexion : {e}")

# 🔥 Fonction pour convertir les images en PDF
def images_to_pdf(folder, pdf_name):
    def sort_key(filename):
        try:
            parts = filename.replace(".png", "").split('_')
            slide_num = int(parts[1])
            index_num = int(parts[2])
            return slide_num, index_num
        except Exception:
            return filename

    image_files = [f for f in os.listdir(folder) if f.endswith(".png")]
    images = [os.path.join(folder, f) for f in sorted(image_files, key=sort_key)]
    
    if not images:
        print("⚠️ Aucune image pour créer le PDF.")
        return

    pdf = FPDF()
    for image_path in images:
        img = Image.open(image_path)
        width, height = img.size
        width_mm, height_mm = width * 0.264583, height * 0.264583
        pdf.add_page(orientation='P')
        pdf.image(image_path, x=0, y=0, w=width_mm, h=height_mm)
    
    safe_pdf_name = "".join(c for c in pdf_name if c.isalnum() or c in (" ", "_", "-")).rstrip()
    pdf_output = f"{safe_pdf_name}.pdf"
    pdf.output(pdf_output, "F")
    print(f"📄 PDF généré : {pdf_output}")
    shutil.rmtree(folder)
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

    images_to_pdf(temp_folder, pdf_title)

# =====================================================
# 4️⃣ Traitement de tous les cours
# =====================================================
for url, nb_slides in cours_info:
    traiter_cours(url, nb_slides)

driver.quit()
print("\n✅ Tous les cours ont été traités avec succès. 🎉")
