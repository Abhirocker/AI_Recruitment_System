from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from create_db import get_db
import sqlite3

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        email = request.form['email']

        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password, name, email) VALUES (?, ?, ?, ?)', 
                        (username, password, name, email))
            db.commit()
            return redirect(url_for('auth.sign_in'))
        except sqlite3.IntegrityError:
            return 'Username already exists.'

    return render_template('sign_up.html')

@auth_blueprint.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_type = request.form.get('login_type')  # Get the login type from the form
        
        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        
        if user and password == user['password']:
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            
            if login_type == 'admin' and user['is_admin']:
                return redirect(url_for('admin.dashboard'))  # Redirect to admin dashboard
            elif login_type == 'user':
                return redirect(url_for('user.user_dashboard'))  # Redirect to user dashboard
            else:
                flash('Invalid login type for this user.')
        else:
            flash('Invalid credentials, please try again.')
    
    return render_template('sign_in.html')

@auth_blueprint.route('/sign_out')
def sign_out():
    session.pop('username', None)
    return redirect(url_for('auth.sign_in'))
