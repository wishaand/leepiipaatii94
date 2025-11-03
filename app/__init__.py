"""Entry point for Flask application"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from sqlalchemy import text
from config import Config

# create extensions at module level so models can import them safely
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'main.login'
csrf = CSRFProtect()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app)

    # Make csrf_token() available in Jinja templates
    app.jinja_env.globals['csrf_token'] = generate_csrf

    # --- Add: test database connection and report to terminal ---
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
        app.logger.info("Database connection successful")
        print("Database connection successful")
    except Exception as e:
        app.logger.error("Database connection failed: %s", e)
        print("Database connection failed:", e)
    # --- End added code ---

    # register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    # register loader (if you use load_user in models)
    from app.models import load_user
    login.user_loader(load_user)

    return app

from app import models
