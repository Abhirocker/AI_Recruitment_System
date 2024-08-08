from flask import Blueprint, render_template, session, redirect, url_for, flash
from create_db import get_db

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
    
    return render_template('admin_dashboard.html')