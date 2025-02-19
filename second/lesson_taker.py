from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import requests
import getpass  # Pour sécuriser la saisie du mot de passe

# Configuration de Selenium
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--disable-logging")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # 0 = ALL, 1 = WARNING, 2 = ERROR, 3 = FATAL
chrome_options.add_argument("--log-level=3")  # 0=ALL, 1=DEBUG, 2=INFO, 3=WARNING
chrome_options.add_argument("--no-sandbox")

# Initialiser le WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Demander les informations de connexion
login_url = "https://reussistonifsi.learnybox.com/connexion/"
email = input("Entrez votre email : ")
password = getpass.getpass("Entrez votre mot de passe : ")  # Masque la saisie du mot de passe

# Se connecter au site
driver.get(login_url)

try:
    # Remplir l'email
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "email"))
    )
    email_input.send_keys(email)

    # Remplir le mot de passe
    password_input = driver.find_element(By.NAME, "password")
    password_input.send_keys(password)

    # Soumettre le formulaire
    password_input.submit()

    print("✅ Connexion réussie !")
    time.sleep(3)  # Laisser le temps de charger la page

except Exception as e:
    print(f"❌ Erreur lors de la connexion : {e}")
    driver.quit()
    exit()

# Demander à l'utilisateur l'URL du premier cours et le nombre de cours
start_url = input("Entrez l'URL du premier cours : ")
num_courses = int(input("Entrez le nombre de cours à récupérer : "))

# Aller au premier cours
driver.get(start_url)

# Création d'un dossier pour sauvegarder les images
output_folder = os.path.join(os.getcwd(), "cours_images")
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Fonction pour télécharger une image
def download_image(img_url, filename):
    try:
        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            with open(os.path.join(output_folder, filename), 'wb') as file:
                file.write(response.content)
            print(f"✅ Image enregistrée : {filename}")
        else:
            print(f"⚠️ Erreur lors du téléchargement de {img_url} (Code {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Erreur de connexion pour {img_url}: {e}")

# Attente pour s'assurer du chargement de la page
wait = WebDriverWait(driver, 15)

# Récupération des images et navigation entre les cours
for i in range(num_courses):
    print(f"📖 Traitement du cours {i+1}...")

    try:
        # Récupérer toutes les images visibles sur la page
        image_elements = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".slick-slide img"))
        )
        
        if image_elements:
            for index, img in enumerate(image_elements):
                img_url = img.get_attribute("src")
                if img_url:
                    filename = f"cours_{i+1}_image_{index+1}.png"
                    download_image(img_url, filename)
        else:
            print("⚠️ Aucune image trouvée pour ce cours.")

        # Aller au cours suivant en cliquant sur la deuxième flèche
        next_buttons = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".btn.btn-success"))
        )

        if len(next_buttons) > 1:
            next_buttons[1].click()  # La deuxième flèche
            print("➡️ Passage au cours suivant...")
        else:
            print("⚠️ Impossible de trouver la deuxième flèche.")
            break

        time.sleep(3)  # Pause pour permettre le chargement du prochain cours

    except Exception as e:
        print(f"❌ Erreur lors du traitement du cours {i+1}: {e}")
        break

# Fermer le navigateur
driver.quit()
print("✅ Script terminé.")
