from flask import Blueprint, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
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
        skills = request.form['skills']
        hashed_password = generate_password_hash(password)

        db = get_db()
        try:
            db.execute('INSERT INTO users (username, password, name, email, skills) VALUES (?, ?, ?, ?, ?)', 
                        (username, hashed_password, name, email, skills))
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

        db = get_db()
        user = db.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()

        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect(url_for('home.home'))
        else:
            return 'Invalid username or password.'

    return render_template('sign_in.html')

@auth_blueprint.route('/sign_out')
def sign_out():
    session.pop('username', None)
    return redirect(url_for('auth.sign_in'))
