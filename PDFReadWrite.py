import PyPDF2
import pandas as pd

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        for page_num in range(num_pages):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
    return text


def write_text_to_file(text, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(text)

pdf_path = 'C:/Users/ADMIN/Desktop/py/Tunnel.pdf'
extracted_text = extract_text_from_pdf(pdf_path)
output_file_path = 'tunnel.txt'  # Specify the path for the output file
write_text_to_file(extracted_text, output_file_path)
#print(extracted_text)
