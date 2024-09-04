from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from create_db import get_db
from datetime import datetime

admin_blueprint = Blueprint('admin', __name__)

def is_admin(username):
    db = get_db()
    user_info = db.execute('SELECT is_admin FROM users WHERE username = ?', (username,)).fetchone()
    return user_info['is_admin'] == 1

@admin_blueprint.route('/admin_dashboard')
def dashboard():
    if 'username' not in session or not is_admin(session['username']):
        flash('You are not authorized to access this page.')
        return redirect(url_for('auth.sign_in'))
    
    # Load existing job applications
    db = get_db()
    job_applications = db.execute('SELECT id, position, company, location, experience_range, description, posted_date FROM job_applications').fetchall()
    return render_template('admin_dashboard.html', job_applications=job_applications)

@admin_blueprint.route('/create_job', methods=['GET', 'POST'])
def create_job():
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('auth.sign_in'))
    
    if request.method == 'POST':
        position = request.form['position']
        company = request.form['company']
        location = request.form['location']
        experience_range = request.form['experience_range']
        description = request.form['description']
        posted_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Get current date and time
        
        db = get_db()
        db.execute('''INSERT INTO job_applications (position, company, location, experience_range, description, posted_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (position, company, location, experience_range, description, posted_date))
        db.commit()
        
        flash('Job application created successfully.')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('create_job.html')

@admin_blueprint.route('/view_job/<int:job_id>')
def view_job(job_id):
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('auth.sign_in'))
    
    db = get_db()
    
    job = db.execute('SELECT * FROM job_applications WHERE id = ?', (job_id,)).fetchone()
    if not job:
        flash('Job application not found.')
        return redirect(url_for('admin.dashboard'))
    
    applications = db.execute('''
        SELECT u.username, ua.resume, ua.similarity_score
        FROM user_applications ua
        JOIN users u ON ua.user_id = u.id
        WHERE ua.job_id = ?
    ''', (job_id,)).fetchall()
    
    return render_template('view_job.html', job=job, applications=applications)

@admin_blueprint.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('auth.sign_in'))
    
    db = get_db()
    job = db.execute('SELECT * FROM job_applications WHERE id = ?', (job_id,)).fetchone()
    
    if not job:
        flash('Job application not found.')
        return redirect(url_for('admin.dashboard'))
    
    if request.method == 'POST':
        position = request.form.get('position')
        company = request.form.get('company')
        location = request.form.get('location')
        experience_range = request.form.get('experience_range')
        description = request.form.get('description')
        posted_date = request.form.get('posted_date')
        
        db.execute('UPDATE job_applications SET position = ?, company = ?, location = ?, experience_range = ?, description = ?, posted_date = ? WHERE id = ?', 
                   (position, company, location, experience_range, description, posted_date, job_id))
        db.commit()
        
        flash('Job application updated successfully.')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('edit_job.html', job=job)

@admin_blueprint.route('/delete_job/<int:job_id>')
def delete_job(job_id):
    if 'username' not in session or not session.get('is_admin'):
        return redirect(url_for('auth.sign_in'))
    
    db = get_db()
    db.execute('DELETE FROM job_applications WHERE id = ?', (job_id,))
    db.commit()
    
    flash('Job application deleted successfully.')
    return redirect(url_for('admin.dashboard'))

@admin_blueprint.route('/interview_evaluation/<string:username>', methods=['POST'])
def interview_evaluation(username):
    db = get_db()

    # Fetch the user application and job details
    application = db.execute('''
        SELECT u.username, ua.resume, ua.similarity_score
        FROM user_applications ua
        JOIN users u ON ua.user_id = u.id
        WHERE u.username = ?
    ''', (username,)).fetchone()

    if not application:
        return "Application not found", 404

    application = dict(application)

    # Render the interview evaluation page
    return render_template('interview_evaluation.html', application=application)

@admin_blueprint.route('/hr_evaluation/<string:username>', methods=['POST'])
def hr_evaluation(username):
    # Fetch the form data for technical evaluation
    tech_total = sum([
        int(request.form.get('mark1', 0)),
        int(request.form.get('mark2', 0)),
        int(request.form.get('mark3', 0)),
        int(request.form.get('mark4', 0)),
        int(request.form.get('mark5', 0))
    ])

    # Pass the data to HR evaluation template
    return render_template('interview_evaluation.html', application={
        'username': username,
        'tech_total': tech_total,
    })

@admin_blueprint.route('/final_evaluation/<string:username>', methods=['POST'])
def final_evaluation(username):
    # Process final evaluation here
    return redirect(url_for('some_other_page'))
