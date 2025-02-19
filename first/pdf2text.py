import PyPDF2
import os

def pdf_to_text(pdf_path, output_path=None):
    """
    Convert a PDF file to a plain text file.

    :param pdf_path: Path to the PDF file.
    :param output_path: Path to save the output text file. If None, the text will be returned.
    :return: Extracted text if output_path is None, otherwise None.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The file {pdf_path} does not exist.")

    # Open the PDF file
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        extracted_text = ""

        # Extract text from each page
        for page_num, page in enumerate(pdf_reader.pages):
            extracted_text += f"--- Page {page_num + 1} ---\n"
            extracted_text += page.extract_text() + "\n\n"

    # Save the text to a file if output_path is provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as text_file:
            text_file.write(extracted_text)
        print(f"Text extracted and saved to {output_path}")
    else:
        return extracted_text

# Example usage
if __name__ == "__main__":
    input_pdf = input("Enter the path to the PDF file: ")
    output_txt = input("Enter the path to save the output text file (leave empty to display text): ")

    try:
        if output_txt.strip():
            pdf_to_text(input_pdf, output_txt)
        else:
            text = pdf_to_text(input_pdf)
            print("\nExtracted text:\n")
            print(text)
    except Exception as e:
        print(f"An error occurred: {e}")