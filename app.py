import os
from flask import Flask
from create_db import init_db
from auth import auth_blueprint
from home import home_blueprint

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_12345'

# Initialize the database
init_db()

# Register blueprints
app.register_blueprint(auth_blueprint)
app.register_blueprint(home_blueprint)

if __name__ == '__main__':
    app.run(debug=True)
