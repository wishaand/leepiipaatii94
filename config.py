import os
from urllib.parse import quote_plus

# .env.example (maak .env op basis hiervan)
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASS = os.getenv("DATABASE_PASS")
DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = os.getenv("DATABASE_PORT", "3306")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# Use PyMySQL driver
DB_PASS_ESC = quote_plus(DATABASE_PASS or "")
SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DATABASE_USER}:{DB_PASS_ESC}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
API_KEY = os.getenv("API_KEY", "REPLACE_WITH_API_KEY")

# opslaan als requirements.txt
Flask
Flask-SQLAlchemy
Flask-Migrate
Flask-Login
python-dotenv
PyMySQL
Werkzeug