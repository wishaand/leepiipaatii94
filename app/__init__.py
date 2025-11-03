"""Entry point for Flask application"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# create extensions at module level so models can import them safely
db = SQLAlchemy()
login = LoginManager()
login.login_view = "main.login"

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)

    # register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # import models here (safe: db & login already defined)
    from app import models  # models may use @login.user_loader

    return app

from app import models
