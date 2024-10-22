import os
from flask import Flask, render_template, send_from_directory
from create_db import init_db
from auth import auth_blueprint
from user import user_blueprint
from admin import admin_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')

# Initialize the database
init_db()

# Register blueprints
app.register_blueprint(auth_blueprint, url_prefix='/auth')
app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(admin_blueprint, url_prefix='/admin')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/animations/<path:filename>')
def animations(filename):
   return send_from_directory('Animations', filename)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if __name__ == '__main__':
    app.run(debug=True)
