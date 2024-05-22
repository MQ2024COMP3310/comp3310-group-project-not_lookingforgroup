from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from pathlib import Path

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__) # Flask app created

    app.config['SECRET_KEY'] = 'secret-key-do-not-reveal' # TODO this shouldn't be here ...Secret key set Used in(session management, CSRF protection)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///photos.db' # String for URI to connect to the database
    CWD = Path(os.path.dirname(__file__)) # Works out the current working directory the script is run from
    app.config['UPLOAD_DIR'] = CWD / "uploads" # Configures the path to the directory where files are uploaded

    db.init_app(app) # associates the db object with the Flask application. It sets up the SQLAlchemy engine, declarative model class, and scoped session

    # blueprint for non-auth parts of app
    from .main import main as main_blueprint # From main.py
    app.register_blueprint(main_blueprint) # Adds the main blueprint implemented in main.py to Flask
        # A blueprint defines a set of related routes and views that can be registered with the main Flask application.
        # By registering it with the app (app.register_blueprint(main_blueprint)), those routes become accessible via the main app’s URL.
    return app
