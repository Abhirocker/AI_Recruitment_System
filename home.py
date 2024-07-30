from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from create_db import get_db
from ai_module import generate_recommendations

home_blueprint = Blueprint('home', __name__)

def get_user_info(username):
    db = get_db()
    user_info = db.execute('SELECT name, email, skills FROM users WHERE username = ?', (username,)).fetchone()
    if user_info:
        return dict(user_info)
    return {}

def get_job_applications(username):
    db = get_db()
    job_applications = db.execute('SELECT position, company FROM job_applications WHERE username = ?', (username,)).fetchall()
    return [dict(row) for row in job_applications]

@home_blueprint.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('auth.sign_in'))

    username = session['username']
    user_info = get_user_info(username)
    job_applications = get_job_applications(username)
    
    if user_info:
        recommended_jobs = generate_recommendations(user_info['skills'])  # AI recommendations
    else:
        recommended_jobs = []

    return render_template('home.html', username=username, user_info=user_info, job_applications=job_applications, recommended_jobs=recommended_jobs)

@home_blueprint.route('/update_profile', methods=['POST'])
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
    return redirect(url_for('home.home'))