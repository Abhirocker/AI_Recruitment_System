import PyPDF2
import docx
import os
# Function to extract text from PDF using PyPDF2
def extract_text_from_pdf(pdf_path):
   text = ""
   with open(pdf_path, 'rb') as file:
       reader = PyPDF2.PdfReader(file)
       for page in reader.pages:
           text += page.extract_text() or ""
   return text
# Function to extract text from Word document
def extract_text_from_docx(docx_path):
   doc = docx.Document(docx_path)
   full_text = []
   for para in doc.paragraphs:
       full_text.append(para.text)
   return '\n'.join(full_text)
# Function to save text to a file
def save_text_to_file(text, output_file_path):
   with open(output_file_path, 'w') as file:
       file.write(text)
# Main function to handle file extraction and saving
def extract_and_save_text(file_path, output_file_path):
   if file_path.endswith('.pdf'):
       text = extract_text_from_pdf(file_path)
   elif file_path.endswith('.docx'):
       text = extract_text_from_docx(file_path)
   else:
       raise ValueError("Unsupported file format")
   save_text_to_file(text, output_file_path)
# Example usage within a Flask context
def handle_uploaded_resume(upload_folder, filename):
   input_file_path = os.path.join(upload_folder, filename)
   output_file_path = os.path.join(upload_folder, 'extracted_text.txt')  # Saving the extracted text in the same folder
   extract_and_save_text(input_file_path, output_file_path)
   return output_file_path
