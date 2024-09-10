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
        'Python', 'Java', 'JavaScript', 'C++', 'SQL', 'HTML', 'CSS', 'LibreOffice Calc', 'QlikView', 'Jira', 'Salesforce', 'IBM SPSS', 'ABBYY FlexiCapture', 'Slack', 'CyberArk', 'Tableau', 'C#', 'Azure DevOps', 'Visual Studio', 'SQL Server', 'ASP.NET Core',
        'Machine Learning', 'AI', 'Data Science', 'Deep Learning', 'NLP', 'Celonis', 'IBM Watson Natural Language Understanding', 'Microsoft Azure ML', 'Salesforce Sales Cloud', 'Salesforce Agile Accelerator', '.NET Framework', 'Linux', 'Entity Framework',
        'Project Management', 'Agile', 'Scrum', 'Git', 'Docker', 'AWS', 'MySQL', 'PostgreSQL', 'Microsoft Excel', 'MS Excel', 'Trello', 'Informatica Cloud', 'JUnit', 'IFTTT', 'Google Sheets', 'Matplotlib', 'Finance and Accounting', 'Docker', 'MongoDB', 'Azure',
        'Powerpoint', 'MS Powerpoint', 'JIRA', 'Github', 'Appian', 'ARIS', 'SAP', 'Wrike', 'Pipedrive', 'Celonis', 'UiPath', 'Microsoft Office', 'Google Workspace', 'Tuleap', 'Quip', 'Balsamiq', 'Zapier', 'vhdl', 'assembler', 'typescript', 'matlab', 'xml', 'tcl',
        'js', 'Ruby', 'Bash', 'Kubernetes', 'Terraform', 'Cloudformation', 'Jenkins', 'Azure Pipelines', 'LAMP stack', 'Nagios', 'RESTful APIS', 'Ansible', 'Zend Framework', 'Azure Monitor', 'Microsoft Azure', 'PowerShell', 'VMware', 'Trello', 'KVM/VZ Virtualization',
        'Groovy', 'Chef', 'NoSQL', 'GitLab CI/CD', 'Bitbucket', 'Prometheus', 'Google Cloud Platform', 'Selenium', 'HashiCorp Vault', 'ElasticSearch', 'AWS (CLI, EC2, S3, RDS)', 'Greenhouse ATS', 'Recruiting coordination', 'ATS (Greenhouse)', 'Recruiting Coordination',
        'Compliance (OFCCP, FMLA, FLSA, unemployment)', 'Employee Retention', 'Employee Coaching', 'LOA, FMLA, PLOA, Disability', 'HRIS (Workday)', 'PHR certification ATS (Workday, Jobvite) Compensation & Benefits Payroll Performance Management', 'HR Software (including Zenefits, and BambooHR)',
        'BambooHR', 'Jobvite', 'Saba Cloud', 'BetterWorks', 'QuickBooks Payroll', 'Qualtrics EmployeeXM', 'ADP Time and Attendance', 'Google Workspace', 'Oracle Talent Management', 'Namely Benefits', 'Spring Boot', 'Maven', 'Confluence', 'Kanbanize', 'Hibernate', ' JavaServer Faces (JSF)',
        'Windows', 'Apache Camel', 'AWS Lambda', 'Apache ActiveMQ', 'AWS API Gateway', 'OpenShift', 'AWS CodePipeline', 'IntelliJ IDEAJUnit', 'Swagger', 'Apache Maven', 'Angular.js', 'UNIX', 'Eclipse', 'Django', 'Node.js', '(REST) APIs', 'Appium', 'PyTest', 'Travis CI', 'BrowserStack', 'Appium',
        'JMeter', 'TestRail', 'Zephyr', 'Gherkin', 'Bugzilla', 'LoadRunner', 'Burp Suit', 'OWASP ZAP', 'GenRocket', 'Apache JMeter', 'TestLodge', 'Delphix', 'Calabash', 'Postman', 'WordPress', 'Adobe Photoshop', 'Illustrator', 'XD', 'Figma', 'Wireframes', 'Mockups', 'Prototypes',
        'Google Analytics', 'A/B Testing', 'macOS', 'Mobile-first design', 'Cross-browser compatibility', 'Flask', 'FastAPI', 'AWS (Redshift, S3)', 'REST APIs (GraphQL)', 'Microsoft Project', 'PMO Manager', 'Power BI', 'Project Planning', 'Resource Management', 'Risk Management',
        'Firewalls', 'IDS/IPS', 'VPNs', 'Antivirus', 'Wireshark', 'Nmap', 'Nessus', 'TCP/IP', 'DNS', 'HTTP/HTTPS', 'SIEM', 'Splunk', 'SNPM', 'CAD', 'SolidWorks', 'Autodesk Inventor', 'MATLAB,', 'Primavera P6', 'ANSYS', 'COMSOL Multiphysics', 'AutoCAD', 'Revit', 'ANSYS Fluen', 'OpenFOAM',
        'PTC Windchill', 'Siemens Teamcenter', 'LabVIEW', 'OSHA Safety Regulations', 'Word', 'ITIL', 'Project Management', 'Process Optimization', 'Microsoft Office Suite', 'Microsoft Word', 'Microsoft Powerpoint', 'Data analysis and reporting', 'Pandas', 'TensorFlow', 'Apache Hadoop', 'Amazon Redshift', 'NLTK', 'Apache Kafka',
        'Machine and Deep Learning', 'Statistical Analysis', 'Processing Large Data Sets', 'Data Visualization', 'Mathematics', 'Data Wrangling', 'SQL (Structured Query Language)', 'Databricks', 'Scikit-learn', 'NLTK (Natural Language Toolkit) Informatica', 'Apache Spark', 'TensorFlow', 'Hadoop', 'Apache Mahout', 'SAS', 'Oracle',
        'Amazon Web Services (AWS)', 'Apache Atlas', 'Jupyter Notebook', 'Python (NumPy, Pandas, Scikit- learn, Keras, Flask)', 'SQL (Redshift, MySQL, Postgres, NoSQL)', 'Pandas', 'R', 'Scala', 'Hadoop', 'SQLite', 'Keras', 'NumPy', 'ggplot2', 'dplyr', 'PyTorch', 'Time Series Forecasting', 'Productionizing Models',
        'Recommendation Engines', 'Customer Segmentation', 'Matplotlib', 'Microsoft Power BI', 'ArcGIS', 'Adobe Illustrator', 'SPSS', 'Shiny', 'Unity3D', 'Supervised Learning', 'linear and logistic regressions', 'decision trees', 'support vector machines (SVM)', 'Unsupervised Learning', 'k- means clustering',
        'principal component analysis (PCA)', 'Apache Airflow', 'SpaCy', 'Spark', 'GCP', 'Amazon Redshift', 'Talend', 'Epic Systems', 'spaCy', 'SVN'
    ]
    
    common_positions = [
        'Agile Business Analyst', 'Business Process Analyst', 'Junior Business Analyst', 'RPA Business Analyst', 'Business Systems Analyst', 'Senior Business Analyst', 'Business Analyst', 'Technical Business Analyst', 'Junior .NET Develope', 'Human Resources Manager',
        'Senior .NET Developer', 'Senior Full Stack Software Developer', 'AWS DevOps Engineer', 'Azure DevOps', 'DevOps Engineer', 'DevOps Manager', 'DevOps Intern', 'Senior DevOps Engineer', 'Human Resources Intern', 'Human Resources Assistant', 'HR Generalist',
        'Senior HR Manager', 'Java Developer', 'Junior Java Developer', 'Java AWS Integration Specialist', 'JAVA BACKEND DEVELOPER', 'Java Developer Intern', 'Senior Java Developer', 'Automation Tester', 'QA Tester', 'Software Tester', 'Tester', 'Senior Web Designer',
        'Junior Web Designer', 'Junior Python Developer', 'Senior Python Developer', 'Python Developer', 'PMO Coordinator', 'PMO Manager', 'Junior Network Security Engineer', 'Senior Network Security Engineer', 'Mechanical Engineer', 'Mechanical Project Engineer',
        'Senior Mechanical Engineer', 'Operations Manager', 'IT Operations Manager', 'Data Scientist', 'Data Scientist Intern', 'Data Science Manager', 'Data Science Director', 'Data Scientist, Analytics', 'Data Scientist Machine Learning Engineer', 'Data Visualization Specialist', 
        'Senior Data Scientist', 'Google Data Scientist', 'Healthcare Data Scientist', 'NLP Data Scientist'
    ]
    
    common_education = [
        'Bachelor of Science in Computer Science', 'B.S. Business', 'Bachelor of Science Business Administration', 'Bachelor of Business Administration Management Information Systems', 'Bachelor of Arts Human Resources Management',
        'Doctor of Philosophy', 'B.S., Computer Science', 'MBA', 'B.A.', 'B.Com', 'B.E', 'B.Tech', 'Bachelor of Science Business', 'Bachelor of Science Computer Science', 'B.S. Computer Science', 'Master of Science Computer Science',
        'Bachelor of Science in Business Human Resource Management', 'Bachelor of Science Software Engineering', 'Bachelor of Science, Computer Science', 'Bachelor of Fine Arts in Graphic Design', 'M.S. Computer Science', 'Bachelor of Science in Information Technology',
        'Bachelor of Science in Cybersecurity', 'Bachelor of Science Mechanical Egineering', 'Bachelor of Science, Mechanical Engineering', 'Diploma', 'Bachelor of Arts Business Administration', 'IT Operations Coordinator', 'Senior Operations Manager', 'Data Science Director',
        'B.S. Mathematics and Economics', 'Bachelor of Science Informatics', 'Data Science Intern', 'Masters degree Statistics', 'B.S. Statistics', 'Bachelor of Arts Data Science', 'Educational Data Scientist', 'B.S. Mathematics and Economics', 'Master of Computational Data Science',
        'Master of Science Data Science', 'Master of Science Health Informatics', 'PhD Natural Language Processing (NLP)'
    ]
    
    common_achievements = [
        'Award', 'Certification', 'Patent', 'Publication', 'Recognition', 
        'Achievement', 'Scholarship', 'Fellowship', 'Rank', 'Runner-up'
    ]
    
    common_certifications = [
        'Certified Business Process Associate (CBPA)', 'Entry Certificate in Business Analysis (ECBA)', 'Salesforce Certified Advanced Administrator', 'PMI Professional in Business Analysis (PMI-PBA)', 'Microsoft Certified: Azure Fundamentals', 'AWS Certified Solutions Architect',
        'Amazon Web Services (AWS) Certified Solutions Architect (CSA)', 'Foundations of Human Resources Management Certificate', 'PMI Agile Certified Practitioner (PMI-ACP)', 'AWS Certified Solutions Architect', 'Oracle Certified Professional, Java SE 11 Developer (OCPJP)',
        'Oracle Certified Professional: Java SE 11 Developer', 'Adobe Certified Expert (ACE) in Photoshop', 'Certified UX Designer', 'Adobe Certified Associate (ACA) in Visual Design', 'Python for Everybody Specialization', 'Certified Associate in Project Management (CAPM)',
        'Project Management Professional (PMP)', 'Certified ScrumMaster (CSM)', 'ITIL Foundation Certification', 'Certified Information Systems Security Professional (CISSP)', 'Certified Ethical Hacker (CEH)', 'Cisco Certified Network Associate (CCNA) Security',
        'CompTIA Security', 'Certified Ethical Hacker (CEH)', 'LEED Certification', 'Six Sigma Certification', 'Certified Reliability Engineer (CRE)', 'PMP Certification', 'Certified Information Systems Manager (CISM)', 'ITIL Expert Certification', 'Project Management Professional (PMP)',
        'ITIL Foundation Certification', 'Open Certified Data Scientist (Open CDS)', 'Google Data Machine Learning', 'B.S. Data Science', 'SAS Certified Data Scientist Certified Analytics Professional (CAP)', 'Certified Machine Learning Engineer (CMLE)', ''
        'AWS', 'Data Science (SAS) Principal Data Scientist (DASCA)'
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
