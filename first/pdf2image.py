import fitz  # PyMuPDF
import os


def pdf_to_images(pdf_path, output_folder, dpi=150):
    """
    Convertit un fichier PDF en images et les enregistre dans un dossier de sortie.

    Args:
        pdf_path (str): Le chemin vers le fichier PDF.
        output_folder (str): Le dossier de sortie pour enregistrer les images.
        dpi (int, optionnel): La résolution des images générées en points par pouce. Par défaut à 150 dpi pour une conversion plus rapide.
    """
    try:
        # Assurez-vous que le dossier de sortie existe
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Ouvrir le PDF avec PyMuPDF
        pdf_document = fitz.open(pdf_path)
        
        # Parcourir chaque page et l'enregistrer en tant qu'image
        for i in range(len(pdf_document)):
            page = pdf_document.load_page(i)
            pix = page.get_pixmap(dpi=dpi, alpha=False)  # Réduire le DPI et désactiver alpha pour accélérer
            image_filename = os.path.join(output_folder, f"page_{i + 1}.jpeg")
            pix.save(image_filename)
            print(f"Image enregistrée : {image_filename}")
    
    except Exception as e:
        print(f"Erreur lors de la conversion du PDF : {e}")


if __name__ == "__main__":
    # Demander à l'utilisateur le chemin du fichier PDF et le dossier de sortie
    pdf_path = input("Veuillez entrer le chemin vers votre fichier PDF : ")
    output_folder = input("Veuillez entrer le chemin vers le dossier de sortie : ")
    
    # Convertir le PDF en images
    pdf_to_images(pdf_path, output_folder)

    print("Conversion terminée avec succès !")
