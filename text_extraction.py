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
            text += page.extract_text() or ''
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

def extract_details_from_resume(text):
    # Define common terms
    common_skills = [
        'Python', 'Java', 'JavaScript', 'C++', 'SQL', 'HTML', 'CSS',
        'Machine Learning', 'AI', 'Data Science', 'Deep Learning', 'NLP',
        'Project Management', 'Agile', 'Scrum', 'Git', 'Docker', 'AWS'
    ]
    
    common_positions = [
        'Software Engineer', 'Data Scientist', 'Product Manager', 'Project Manager', 
        'Business Analyst', 'DevOps Engineer', 'Data Analyst', 'Project Engineer', 
        'Full Stack Developer'
    ]
    
    common_education = [
        'B.Sc', 'M.Sc', 'Ph.D', 'Bachelor of Science', 'Master of Science',
        'Doctor of Philosophy', 'MBA', 'B.A.', 'B.Com', 'B.E'
    ]
    
    common_achievements = [
        'Award', 'Certification', 'Patent', 'Publication', 'Recognition', 
        'Achievement', 'Scholarship', 'Fellowship', 'Rank', 'Runner-up'
    ]
    
    common_certifications = [
        'Certified', 'Certification', 'AWS Certified', 'PMP', 'Scrum Master',
        'Six Sigma', 'Data Scientist Certified', 'Cisco Certified', 'Microsoft Certified'
    ]
    
    # Process the text with spaCy
    doc = nlp(text)
    
    # Initialize containers for detected information
    detected_skills = set()
    detected_position = None
    detected_education = None
    detected_achievements = set()
    detected_certifications = set()
    detected_location = None
    detected_experience = None
    
    # Extract information based on common terms
    for token in doc:
        if token.text in common_skills:
            detected_skills.add(token.text)
        if token.text in common_positions and not detected_position:
            detected_position = token.text
        if token.text in common_education and not detected_education:
            detected_education = token.text
        if token.text in common_achievements:
            detected_achievements.add(token.text)
        if token.text in common_certifications:
            detected_certifications.add(token.text)
    
    # Extract sections based on common resume headings
    sections = ['EDUCATION', 'EXPERIENCE', 'PROJECTS', 'ACHIEVEMENTS', 'CERTIFICATIONS']
    text_upper = text.upper()
    
    section_starts = {section: text_upper.find(section) for section in sections if section in text_upper}
    section_end_indexes = {section: len(text) for section in sections}
    
    for i, section in enumerate(sections):
        if section in section_starts:
            start = section_starts[section] + len(section)
            next_section = sections[i + 1] if i + 1 < len(sections) else None
            end = section_starts[next_section] if next_section in section_starts else len(text)
            section_text = text[start:end].strip()
            
            if section == 'EDUCATION':
                detected_education = extract_highest_education(section_text, common_education)
            elif section == 'EXPERIENCE':
                detected_position = extract_position(section_text, common_positions)
                detected_location = extract_location(section_text)
                detected_experience = extract_experience(section_text)
            elif section == 'PROJECTS':
                # Optionally process projects if needed
                pass
            elif section == 'ACHIEVEMENTS':
                detected_achievements = extract_achievements_from_text(section_text, common_achievements)
            elif section == 'CERTIFICATIONS':
                detected_certifications = extract_certifications_from_text(section_text, common_certifications)
    
    return {
        'skills': ', '.join(detected_skills),
        'last_position': detected_position,
        'location': detected_location,
        'education': detected_education,
        'experience': detected_experience,
        'achievements': ', '.join(detected_achievements),
        'certifications': ', '.join(detected_certifications)
    }

def extract_highest_education(text, common_education):
    detected_education = None
    for education in common_education:
        if education in text:
            detected_education = education
    return detected_education

def extract_position(text, common_positions):
    detected_position = None
    for line in text.split('\n'):
        for position in common_positions:
            if position in line:
                detected_position = position
                break
        if detected_position:
            break
    return detected_position

def extract_location(text):
    detected_location = None
    lines = text.split('\n')
    
    # Example pattern to detect location; you can adjust this based on how locations are formatted in resumes
    for line in lines:
        # Simple heuristic: Location might follow a position or be in a specific format
        if any(keyword in line.lower() for keyword in ['location', 'based in', 'residence']):
            detected_location = line.strip()
            break
            
    return detected_location


def extract_experience(text):
    # Keywords or patterns for years of experience
    experience_keywords = ['years of experience', 'years experience', 'years in', 'years working']
    
    for line in text.split('\n'):
        for keyword in experience_keywords:
            if keyword in line.lower():
                # Extract the first number found in the line as the experience range
                experience = [int(s) for s in line.split() if s.isdigit()]
                if experience:
                    return f"{experience[0]}+ years"
    return None

def extract_achievements_from_text(text, common_achievements):
    achievements = set()
    for achievement in common_achievements:
        if achievement in text:
            achievements.add(achievement)
    return achievements

def extract_certifications_from_text(text, common_certifications):
    certifications = set()
    for certification in common_certifications:
        if certification in text:
            certifications.add(certification)
    return certifications
