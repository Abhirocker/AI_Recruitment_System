import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, current_app
from create_db import get_db
import re
import pickle
from datetime import datetime
from werkzeug.utils import secure_filename
from text_extraction import extract_text_from_file, extract_details_from_resume
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define file paths for models and encoders
label_encoder_path = "models/label_encoder.pkl"
tfidf_path = "models/tfidf.pkl"
clf_path = "models/clf.pkl"

# Load the models and encoders
tfidf = pickle.load(open(tfidf_path, 'rb'))
clf = pickle.load(open(clf_path, 'rb'))
le = pickle.load(open(label_encoder_path, 'rb'))

user_blueprint = Blueprint('user', __name__)
admin_blueprint = Blueprint('admin', __name__)
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'pages', 'txt', 'rtf'}
UPLOAD_FOLDER = 'uploads'

def calculate_cosine_similarity(job_description, resume_text):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([job_description, resume_text])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_resume(file):
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
            os.makedirs(current_app.config['UPLOAD_FOLDER'])
        file.save(file_path)
        return file_path
    return None

def predict_label_from_file(filepath):
    # Extract text from resume
    resume_text = extract_text_from_file(filepath)
    
    # Clean the data and transform using TF-IDF
    input_features = tfidf.transform([resume_text])
    
    # Predict the label
    prediction_id = clf.predict(input_features)[0]
    predicted_label = le.inverse_transform([prediction_id])[0]
    
    return predicted_label

# User ---------------------------------------------------------------------------- Page
# -------------------------------------Dashboard----------------------------------------

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_info(username):
    db = get_db()
    user_info = db.execute('''
        SELECT name, email, skills, last_position, education, achievements, certifications, location, experience
        FROM users
        WHERE username = ?
    ''', (username,)).fetchone()
    return dict(user_info)

def get_job_applications(username):
    db = get_db()
    job_applications = db.execute('''
        SELECT ja.position, ja.company
        FROM job_applications ja
        JOIN user_applications ua ON ja.id = ua.job_id
        JOIN users u ON ua.user_id = u.id
        WHERE u.username = ?
    ''', (username,)).fetchall()
    return job_applications

@user_blueprint.route('/user_dashboard')
def user_dashboard():
    if 'username' not in session:
        return redirect(url_for('auth.sign_in'))

    username = session['username']
    user_info = get_user_info(username)
    job_applications = get_job_applications(username)

    return render_template('user_dashboard.html', username=username, user_info=user_info, job_applications=job_applications) #recommended_jobs=recommended_jobs)

@user_blueprint.route('/update_profile', methods=['POST'])
def update_profile():
    if 'username' not in session:
       return redirect(url_for('auth.sign_in'))
   
    username = session['username']
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    skills = request.form.get('skills', '')
    last_position = request.form.get('last_position', '')
    education = request.form.get('education', '')
    achievements = request.form.get('achievements', '')
    certifications = request.form.get('certifications', '')
    location = request.form.get('location', '')
    experience = request.form.get('experience', '')
   
    db = get_db()
    db.execute('''
        UPDATE users
        SET name = ?, email = ?, skills = ?, last_position = ?, education = ?, achievements = ?, certifications = ?, location = ?, experience = ?
        WHERE username = ?
    ''', (name, email, skills, last_position, education, achievements, certifications, location, experience, username))
    db.commit()
    
    flash('Profile updated successfully!')  # Flash message after updating the profile
    return redirect(url_for('user.user_dashboard'))

@user_blueprint.route('/upload_resume', methods=['POST'])
def upload_resume():
    if 'username' not in session:
        return redirect(url_for('auth.sign_in'))
    
    if 'resume' not in request.files:
        flash('No file part')
        return redirect(url_for('user.user_dashboard'))
    
    file = request.files['resume']
    if file.filename == "":
        flash('No selected file')
        return redirect(url_for('user.user_dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        relative_filepath = os.path.relpath(filepath, upload_folder)
        relative_filepath = os.path.join('uploads', relative_filepath)
        
        # Save the file path in the session
        session['resume_filepath'] = relative_filepath
        
        # Predict label from the resume (without saving to the database)
        predicted_label = predict_label_from_file(filepath)
        session['predicted_label'] = predicted_label 
        print(f"Predicted Label: {predicted_label}")
        
        # Extract text from the file
        text = extract_text_from_file(filepath)
        details = extract_details_from_resume(text)
        username = session['username']
        db = get_db()
        
        db.execute('''
            UPDATE users
            SET skills = ?, last_position = ?, education = ?, achievements = ?, certifications = ?, location = ?, experience = ?
            WHERE username = ?
        ''', (details['skills'], details['last_position'], details['education'], 
              details['achievements'], details['certifications'], details['location'], 
              details.get('experience', ''), username))
        db.commit()
        
        flash('Resume uploaded successfully!')  # Flash message after uploading the resume
        return redirect(url_for('user.user_dashboard'))
    
    flash('Invalid file type')
    return redirect(url_for('user.user_dashboard'))

@user_blueprint.route('/predicted_job_match', methods=['GET'])
def predicted_job_match():
    if 'username' not in session:
        return redirect(url_for('auth.sign_in'))
    
    db = get_db()
    
    predicted_label = session.get('predicted_label', '')
    if not predicted_label:
        flash('No predicted label found. Please upload your resume first.')
        return redirect(url_for('user.user_dashboard'))
    
    if predicted_label:
        # Fetch jobs based on the position/title
        matching_jobs = db.execute('''
            SELECT id, position, company, location, experience_range, description, posted_date
            FROM job_applications
            WHERE LOWER(position) LIKE LOWER(?) OR LOWER(description) LIKE LOWER(?)
        ''', (f'%{predicted_label.lower()}%', f'%{predicted_label.lower()}%')).fetchall()
        
        # Convert results to dictionaries
        matching_jobs = [dict(job) for job in matching_jobs]
        # Filter results in Python
        matched_query_words = re.compile(r'\b' + re.escape(predicted_label.lower()) + r'\b', re.IGNORECASE)
        matching_jobs = [job for job in matching_jobs if matched_query_words.search(job['position']) or matched_query_words.search(job['description'])]
        
    else:
        matching_jobs = []
    print("Predicted Label:", predicted_label)
    
    # Fetch user info
    user_info = db.execute('''
        SELECT name, email, location, experience, skills, last_position, education, achievements, certifications 
        FROM users 
        WHERE username = ?
    ''', (session['username'],)).fetchone()
    
    if user_info:
        user_info = dict(user_info)  # Convert Row object to dict
    else:
        user_info = {}
    
    # Render the jobs in a template (assuming you have a template called 'job_list.html')
    return render_template('user_dashboard.html', predicted_jobs=matching_jobs, user_info=user_info)

@user_blueprint.route('/manual_search', methods=['GET'])
def manual_search():
    if 'username' not in session:
        return redirect(url_for('auth.sign_in'))
    
    search_query = request.args.get('query', '').strip()
    db = get_db()
    
    if search_query:
        # Search jobs based on the position/title
        jobs = db.execute('''
            SELECT id, position, company, location, experience_range, description, posted_date
            FROM job_applications
            WHERE LOWER(position) LIKE LOWER(?) OR LOWER(description) LIKE LOWER(?)
        ''', (f'%{search_query.lower()}%', f'%{search_query.lower()}%')).fetchall()
        
        # Convert results to dictionaries
        jobs = [dict(job) for job in jobs]
        
        # Filter results in Python
        search_query_words = re.compile(r'\b' + re.escape(search_query.lower()) + r'\b', re.IGNORECASE)
        jobs = [job for job in jobs if search_query_words.search(job['position']) or search_query_words.search(job['description'])]
    else:
        jobs = []
    
    # Fetch user info for display
    user_info = db.execute('SELECT name, email, location, experience, skills, last_position, education, achievements, certifications FROM users WHERE username = ?', (session['username'],)).fetchone()
    if user_info:
        user_info = dict(user_info)
    else:
        user_info = {}
    
    return render_template('user_dashboard.html', manual_jobs=jobs, user_info=user_info)

@user_blueprint.route('/apply/<int:job_id>', methods=['POST'])
def apply(job_id):
    resume_filepath = session.get('resume_filepath')
    
    if not resume_filepath:
        flash('Resume file path not found')
        return redirect(url_for('user.user_dashboard'))
    
    # Process the resume file path
    try:
        resume_text = extract_text_from_file(resume_filepath)
    except Exception as e:
        flash(f'Error extracting text from file: {e}')
        return redirect(url_for('user.user_dashboard'))
    
    db = get_db()
    
    job_description_result = db.execute('SELECT description FROM job_applications WHERE id = ?', (job_id,)).fetchone()
    
    if not job_description_result:
        flash('Job not found')
        return redirect(url_for('user.user_dashboard'))
    
    job_description = job_description_result['description']
    
    # Calculate cosine similarity score
    similarity_score = calculate_cosine_similarity(job_description, resume_text)
    print(similarity_score)
    
    username = session.get('username')
    
    if username:
        user_id_result = db.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()

        if user_id_result:
            user_id = user_id_result['id']
            
            db.execute('''
                INSERT INTO user_applications (user_id, job_id, resume, similarity_score)
                VALUES (?, ?, ?, ?)
            ''', (user_id, job_id, resume_filepath, similarity_score))
            
            db.commit()
            
            return redirect(url_for('user.view_job_description', job_id=job_id))
        else:
            return "User not found", 404
    else:
        return "User not logged in", 403
    
# View ---------------------------------------------------------------------------- Page
# -------------------------------Description--------------------------------------------

@user_blueprint.route('/view_job_description/<int:job_id>')
def view_job_description(job_id):
    db = get_db()

    # Fetch the job details using job_id
    job = db.execute('''
        SELECT id, position, company, location, experience_range, description, posted_date
        FROM job_applications
        WHERE id = ?
    ''', (job_id,)).fetchone()

    # Fetch the current user's application for this job, if it exists
    user_info = db.execute('''
        SELECT u.name, u.email, u.location, u.experience, u.skills, u.last_position, u.education, 
               u.achievements, u.certifications, ua.resume 
        FROM users u 
        JOIN user_applications ua ON u.id = ua.user_id
        WHERE ua.job_id = ? AND u.username = ?
    ''', (job_id, session.get('username'))).fetchone()

    if user_info:
        user_info = dict(user_info)

    if session.get('is_admin'):
        # Fetch all other applications related to this job, excluding the application_date
        applications = db.execute('''
            SELECT u.username, ua.resume, ua.similarity_score
            FROM user_applications ua
            JOIN users u ON ua.user_id = u.id
            WHERE ua.job_id = ?
        ''', (job_id,)).fetchall()
        
        # Print fetched data for debugging
        for application in applications:
            print(f"Fetched application: {dict(application)}")
        applications = [dict(application) for application in applications]
    else:
        applications = None

    # Render the job details page
    if job:
        job = dict(job)
        return render_template('view_job.html', job=job, user_info=user_info)
    else:
        return "Job not found", 404
    