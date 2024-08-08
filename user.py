import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, current_app
from create_db import get_db
from ai_module import generate_recommendations
import PyPDF2
from werkzeug.utils import secure_filename
from text_extraction import extract_text_from_file, extract_skills_from_resume

user_blueprint = Blueprint('user', __name__)
admin_blueprint = Blueprint('admin', __name__)
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'pages', 'txt', 'rtf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_user_info(username):
    db = get_db()
    user_info = db.execute('SELECT name, email, skills FROM users WHERE username = ?', (username,)).fetchone()
    return dict(user_info)

def get_job_applications(username):
    db = get_db()
    job_applications = db.execute('SELECT position, company FROM job_applications WHERE username = ?', (username,)).fetchall()
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
    name = request.form['name']
    email = request.form['email']
    skills = request.form['skills']

    db = get_db()
    db.execute('UPDATE users SET name = ?, email = ?, skills = ? WHERE username = ?', (name, email, skills, username))
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
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('user.user_dashboard'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from the file
        text = extract_text_from_file(filepath)
        
        skills = extract_skills_from_resume(text)
        username = session['username']
        
        db = get_db()
        db.execute('UPDATE users SET skills = ? WHERE username = ?', (skills, username))
        db.commit()
        
        flash('Profile updated successfully')
        return redirect(url_for('user.user_dashboard'))
    
    flash('Invalid file type')
    return redirect(url_for('user.user_dashboard'))


