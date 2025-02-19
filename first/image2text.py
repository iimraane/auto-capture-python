import pytesseract
from PIL import Image
import os

def extract_text_from_image(image_path):
    """
    Extract text from an image using Tesseract OCR.

    Parameters:
    - image_path (str): Path to the image file.

    Returns:
    - str: Extracted text from the image.
    """
    # Open the image file
    try:
        image = Image.open(image_path)
    except FileNotFoundError:
        raise Exception(f"The file {image_path} was not found.")

    # Use Tesseract to extract text
    extracted_text = pytesseract.image_to_string(image)

    return extracted_text

def extract_text_from_folder(folder_path, output_file):
    """
    Extract text from all images in a folder and save to a text file.

    Parameters:
    - folder_path (str): Path to the folder containing images.
    - output_file (str): Path to the output text file.
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        for index, image_name in enumerate(sorted(os.listdir(folder_path))):
            image_path = os.path.join(folder_path, image_name)
            if os.path.isfile(image_path):
                try:
                    text = extract_text_from_image(image_path)
                    file.write(f"------ Page {index + 1} ------\n")
                    file.write(text + "\n\n")
                except Exception as e:
                    file.write(f"------ Page {index + 1} ------\n")
                    file.write(f"Failed to process {image_name}: {e}\n\n")

# Example usage
if __name__ == "__main__":
    try:
        folder_path = input("Enter the path to the folder containing images: ")
        output_file = input("Enter the path to save the extracted text file: ")
        extract_text_from_folder(folder_path, output_file)
        print(f"Text extracted and saved to {output_file}")
    except Exception as e:
        print(f"Failed to extract text: {e}")
