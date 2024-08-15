import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, current_app
from create_db import get_db
from ai_module import generate_recommendations
import PyPDF2
from werkzeug.utils import secure_filename
from text_extraction import extract_text_from_file, extract_details_from_resume

user_blueprint = Blueprint('user', __name__)
admin_blueprint = Blueprint('admin', __name__)
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'pages', 'txt', 'rtf'}

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
    
    if user_info:
        recommended_jobs = generate_recommendations(user_info['skills'])  # AI recommendations
    else:
        recommended_jobs = []

    return render_template('user_dashboard.html', username=username, user_info=user_info, job_applications=job_applications, recommended_jobs=recommended_jobs)

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

    print(f"Updating profile for {username}:")
    print(f"Name: {name}")
    print(f"Email: {email}")
    print(f"Skills: {skills}")
    print(f"Last Position: {last_position}")
    print(f"Education: {education}")
    print(f"Achievements: {achievements}")
    print(f"Certifications: {certifications}")
    print(f"Location: {location}")
    print(f"Experience: {experience}")
   
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
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
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
