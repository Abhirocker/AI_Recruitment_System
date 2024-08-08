import os
from flask import Flask, redirect, url_for
from create_db import init_db
from auth import auth_blueprint
from user import user_blueprint
from admin import admin_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_12345'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

# Initialize the database
init_db()

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(admin_blueprint, url_prefix='/admin')

@app.route('/')
def index():
    return redirect(url_for('auth.sign_in'))

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=True)
