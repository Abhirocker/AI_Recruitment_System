import os
import spacy
import PyPDF2
from docx import Document
import subprocess

# Load the spaCy model
nlp = spacy.load('en_core_web_sm')

def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(filepath)
    elif ext in ['.doc', '.docx']:
        return extract_text_from_doc(filepath)
    elif ext in ['.txt', '.rtf']:
        return extract_text_from_txt(filepath)
    elif ext == '.pages':
        pdf_filepath = convert_pages_to_pdf(filepath)
        return extract_text_from_pdf(pdf_filepath)
    else:
        raise ValueError('Unsupported file type')

def extract_text_from_pdf(filepath):
    text = ''
    with open(filepath, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_doc(filepath):
    doc = Document(filepath)
    return '\n'.join([para.text for para in doc.paragraphs])

def extract_text_from_txt(filepath):
    with open(filepath, 'r') as file:
        return file.read()
    
def convert_pages_to_pdf(filepath):
    temp_dir = 'temp_pages'
    os.makedirs(temp_dir, exist_ok=True)
    subprocess.run(['soffice', '--headless', '--convert-to', 'pdf', filepath, '--outdir', temp_dir], check=True)
    pdf_filepath = os.path.join(temp_dir, os.path.splitext(os.path.basename(filepath))[0] + '.pdf')
    return pdf_filepath

def extract_skills_from_resume(text):
    # List of common skills
    common_skills = [
        'Python', 'Java', 'JavaScript', 'C++', 'SQL', 'HTML', 'CSS',
        'Machine Learning', 'AI', 'Data Science', 'Deep Learning', 'NLP',
        'Project Management', 'Agile', 'Scrum', 'Git', 'Docker', 'AWS'
    ]
    
    # Process the text with spaCy
    doc = nlp(text)
    
    # Extract skills from the text
    detected_skills = set()
    for token in doc:
        if token.text in common_skills:
            detected_skills.add(token.text)
    
    # Return the skills as a comma-separated string
    return ', '.join(detected_skills)
