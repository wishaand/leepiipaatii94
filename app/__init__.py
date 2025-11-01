"""Entry point for Flask application"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS, SECRET_KEY

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "main.login"

def create_app():
    app = Flask(__name__)
    app.config.from_object("config")
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    return app
