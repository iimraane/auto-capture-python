import time
import os
from PIL import ImageGrab, ImageChops, ImageStat

def images_sont_differentes(img1, img2, seuil=5):
    # Convertir les images en niveaux de gris
    img1_gray = img1.convert('L')
    img2_gray = img2.convert('L')
    # Redimensionner les images pour réduire les détails
    img1_small = img1_gray.resize((100, 100))
    img2_small = img2_gray.resize((100, 100))
    # Calculer la différence entre les images
    diff = ImageChops.difference(img1_small, img2_small)
    # Calculer la moyenne des pixels de la différence
    stat = ImageStat.Stat(diff)
    diff_mean = stat.mean[0]
    # Retourner True si la différence moyenne dépasse le seuil
    return diff_mean > seuil

# Initialiser le compteur
compteur = 1

# Nom du dossier pour stocker les captures
dossier_captures = 'screenshot_taken'

# Créer le dossier s'il n'existe pas
if not os.path.exists(dossier_captures):
    os.makedirs(dossier_captures)
    print(f"Dossier créé : {dossier_captures}")

# Prendre la première capture d'écran
capture_precedente = ImageGrab.grab()

while True:
    time.sleep(1)  # Ajustez l'intervalle si nécessaire
    # Prendre une nouvelle capture d'écran
    capture_actuelle = ImageGrab.grab()
    # Comparer avec la capture précédente
    if images_sont_differentes(capture_precedente, capture_actuelle, seuil=5):
        # Chemin complet du fichier
        nom_fichier = f"capture_{compteur:04d}.png"
        chemin_complet = os.path.join(dossier_captures, nom_fichier)
        capture_actuelle.save(chemin_complet)
        print(f"Capture enregistrée : {chemin_complet}")
        compteur += 1  # Incrémenter le compteur
    # Mettre à jour la capture précédente
    capture_precedente = capture_actuelle
