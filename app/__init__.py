"""Entry point for Flask application"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_wtf.csrf import generate_csrf
from flask_migrate import Migrate  # Nieuw
from sqlalchemy import text
from config import Config

# create extensions at module level so models can import them safely
db = SQLAlchemy()
login = LoginManager()
login.login_view = 'main.login'
csrf = CSRFProtect()
migrate = Migrate()  # Nieuw

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # veilige engine-opties
    app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {"pool_pre_ping": True, "pool_recycle": 280})

    db.init_app(app)
    login.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)  # Nieuw

    # Make csrf_token() available in Jinja templates
    app.jinja_env.globals['csrf_token'] = generate_csrf

    # --- Add: test database connection and create tables if needed ---
    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))
            # Maak tabellen aan als ze niet bestaan
            db.create_all()
            app.logger.info("Database connection successful")
            print("✅ Database connection successful - tabellen zijn aangemaakt/gecontroleerd")
    except Exception as e:
        app.logger.error("Database connection failed: %s", e)
        print(f"❌ Database connection failed: {e}")
    # --- End added code ---

    # register blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.upload import bp as upload_bp
    app.register_blueprint(upload_bp, url_prefix='/upload')
    
    # register loader (if you use load_user in models)
    from app.models import load_user
    login.user_loader(load_user)

    return app
app = create_app()



