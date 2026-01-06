import os
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
    SFTP_PASSWORD = os.getenv("SFTP_PASSWORD")

    # Database (MySQL via PyMySQL)
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD") or ""
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME")

    # Valideer database configuratie
    if not all([DB_USER, DB_NAME]):
        print("⚠️  WAARSCHUWING: Database configuratie ontbreekt!")
        print("   Maak een .env bestand aan met: DB_USER, DB_PASSWORD, DB_HOST, DB_NAME")
        # Fallback naar SQLite voor development als MySQL niet is geconfigureerd
        SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
        print("   Gebruikt SQLite als fallback (app.db)")
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # forceer engine options zodat pool oude verbindingen test/vervangt
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280
    }

    # Nextcloud configuratie
    NEXTCLOUD_SERVER_URL = os.getenv("NEXTCLOUD_SERVER_URL", "https://kai.nl.tab.digital")
    NEXTCLOUD_USERNAME = os.getenv("NEXTCLOUD_USERNAME", "emre.pasa@hva.nl")
    NEXTCLOUD_PASSWORD = os.getenv("NEXTCLOUD_PASSWORD", "Emre@@2005")
    NEXTCLOUD_FOLDER = os.getenv("NEXTCLOUD_FOLDER", "EuroVault")

    # App security
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-replace-in-prod")
    WTF_CSRF_ENABLED = False
