"""Entry point for Flask application"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login = LoginManager()
login.login_view = "main.login"

def create_app(config_class=None):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)

    # import models after db/login are initialized and register loader
    from app import models
    login.user_loader(models.load_user)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    return app

from app import models
