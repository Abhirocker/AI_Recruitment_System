from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from create_db import get_db
from datetime import datetime, timedelta
import random

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

# Interview ---------------------------------------------------------------------------- Page
# -------------------------------------Evaluation--------------------------------------------

@admin_blueprint.route('/interview_evaluation/<string:username>', methods=['GET', 'POST'])
def interview_evaluation(username):
    db = get_db()
    
    # Fetch the job details using job_id
    job = db.execute('''
        SELECT id, position, company, location, experience_range, description, posted_date
        FROM job_applications
        WHERE id = ?
    ''', (username,)).fetchone()

    # Fetch the current user's application for this job, if it exists
    user_info = db.execute('''
        SELECT u.name, u.email, u.location, u.experience, u.skills, u.last_position, u.education, 
               u.achievements, u.certifications, ua.resume 
        FROM users u 
        JOIN user_applications ua ON u.id = ua.user_id
        WHERE ua.job_id = ? AND u.username = ?
    ''', (username, session.get('username'))).fetchone()

    if user_info:
        user_info = dict(user_info)

    # Fetch the user application and job details
    application = db.execute('''
        SELECT u.name, u.username, ua.resume, ua.similarity_score
        FROM user_applications ua
        JOIN users u ON ua.user_id = u.id
        WHERE u.username = ?
    ''', (username,)).fetchone()

    if not application:
        return "Application not found", 404

    application = dict(application)

    if request.method == "POST":
        # Fetch the form data for technical evaluation
        marks = [
            request.form.get('mark1', '0'),
            request.form.get('mark2', '0'),
            request.form.get('mark3', '0'),
            request.form.get('mark4', '0'),
            request.form.get('mark5', '0')
        ]

        try:
            tech_marks = [int(mark) for mark in marks]
        except ValueError as e:
            print(f"Error converting marks: {e}")  # Debugging line
            tech_marks = [0] * len(marks)

        tech_total = sum(tech_marks)

        application['tech_total'] = tech_total

        return render_template('interview_evaluation.html', application=application)

    return render_template('interview_evaluation.html', application=application)

@admin_blueprint.route('/hr_evaluation/<string:username>', methods=['GET','POST'])
def hr_evaluation(username):
    db = get_db()

    application = db.execute('''
        SELECT u.name, u.username, ua.resume, ua.similarity_score
        FROM user_applications ua
        JOIN users u ON ua.user_id = u.id
        WHERE u.username = ?
    ''', (username,)).fetchone()

    if not application:
        return "Application not found", 404

    name = application['name']
    similarity_score = application['similarity_score']

    tech_total = int(request.form.get('tech_total', 0))
    final_total = tech_total
    
    if request.method == "POST":
        # Fetch the form data for technical evaluation
        hr_marks = [
            request.form.get('hr_mark1', '0'),
            request.form.get('hr_mark2', '0'),
            request.form.get('hr_mark3', '0'),
            request.form.get('hr_mark4', '0')
        ]

        try:
            hr_total = [int(hr_mark) for hr_mark in hr_marks]
        except ValueError as e:
            print(f"Error converting marks: {e}")  # Debugging line
            hr_total = [0] * len(hr_marks)

        final_total = (sum(hr_total) + tech_total)

    # Pass the data to HR evaluation template
    return render_template('interview_evaluation.html', application={
        'name': name,
        'username': username,
        'similarity_score': similarity_score,
        'final_total': final_total,
    })

# Final candidates -------------------------------------------------------- starts here
# ---------------------------------------------------------------------------------------

@admin_blueprint.route('/reject_candidate/<string:username>', methods=['POST'])
def reject_candidate(username):
    # No need to delete candidate details, just redirect
    return redirect(url_for('admin.dashboard', username=username))

@admin_blueprint.route('/select_candidate/<string:username>', methods=['POST'])
def select_candidate(username):
    db = get_db()
    
    # Fetch candidate's name from the users table
    candidate = db.execute('SELECT name FROM users WHERE username = ?', (username,)).fetchone()
    candidate_name = candidate['name'] if candidate else None

    # Fetch job title (position) by joining user_applications and job_applications
    job_application = db.execute('''
        SELECT ja.position 
        FROM job_applications ja
        JOIN user_applications ua ON ja.id = ua.job_id
        JOIN users u ON ua.user_id = u.id
        WHERE u.username = ?
    ''', (username,)).fetchone()
    job_title = job_application['position'] if job_application else None

    # Generate a unique 6-digit employee ID
    while True:
        employee_id = '{:06d}'.format(random.randint(0, 999999))
        existing_id = db.execute('SELECT * FROM selected_candidates WHERE employee_id = ?', (employee_id,)).fetchone()
        if not existing_id:
            break

    # Set date of joining as 7 days from today's date
    date_of_joining = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    # Insert the selected candidate into the `selected_candidates` table
    db.execute('''
        INSERT INTO selected_candidates (name, employee_id, job_title, date_of_joining, position)
        VALUES (?, ?, ?, ?, ?)
    ''', (candidate_name, employee_id, job_title, date_of_joining, job_title))
    
    db.commit()
    db.close()

    # Redirect to company home page
    return redirect(url_for('admin.company_home'))

@admin_blueprint.route('/company_home', methods=['GET'])
def company_home():
    db = get_db()

    # Fetch all selected candidates
    candidates = db.execute('SELECT * FROM selected_candidates').fetchall()

    db.close()

    return render_template('company_home.html', candidates=candidates)

@admin_blueprint.route('/save_candidate/<int:id>', methods=['POST'])
def save_candidate(id):
    db = get_db()

    # Fetch updated candidate details from the form
    name = request.form['name']
    employee_id = request.form['employee_id']
    job_title = request.form['job_title']
    date_of_joining = request.form['date_of_joining']
    position = request.form['position']

    # Update the selected candidate's details in the database
    db.execute('''
        UPDATE selected_candidates
        SET name = ?, employee_id = ?, job_title = ?, date_of_joining = ?, position = ?
        WHERE id = ?
    ''', (name, employee_id, job_title, date_of_joining, position, id))

    db.commit()
    db.close()

    # Redirect back to company home
    return redirect(url_for('admin.company_home'))

@admin_blueprint.route('/update_candidate_position', methods=['POST'])
def update_candidate_position():
    db = get_db()
    
    candidates = db.execute('SELECT employee_id FROM selected_candidates').fetchall()
    
    for candidate in candidates:
        employee_id = candidate['employee_id']
        new_position = request.form.get(f'position_{employee_id}')
        
        if new_position:
            db.execute('''
                UPDATE selected_candidates
                SET position = ?
                WHERE employee_id = ?
            ''', (new_position, employee_id))
    
    db.commit()
    db.close()

    return redirect(url_for('admin.company_home'))

@admin_blueprint.route('/delete_candidate/<int:employee_id>', methods=['POST'])
def delete_candidate(employee_id):
    db = get_db()
    
    db.execute('DELETE FROM selected_candidates WHERE employee_id = ?', (employee_id,))
    
    db.commit()
    db.close()
    
    return redirect(url_for('admin.company_home'))
