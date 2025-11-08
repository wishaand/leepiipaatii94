import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    # HBO-ICT API
    API_URL = os.getenv("API_URL")
    API_KEY = os.getenv("API_KEY")
    API_SCOPE = os.getenv("API_SCOPE")

    # SFTP
    SFTP_HOST = os.getenv("SFTP_HOST")
    SFTP_PORT = int(os.getenv("SFTP_PORT", 3322))
    SFTP_USER = os.getenv("SFTP_USER")
    SFTP_PASSWORD = os.getenv("SFTP_PASSWORD")  # keep secret

    # Database (MySQL via PyMySQL)
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD") or ""
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # forceer engine options zodat pool oude verbindingen test/vervangt
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280  # optioneel, in seconden
    }

    # App security
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-replace-in-prod")

    WTF_CSRF_ENABLED = False
