from app import db                 # Database
from app.models import UploadLog   # UploadLog tabel
from datetime import datetime, timedelta
from flask import current_app
import os


class UploadLogService:
    # Deze class regelt alles met upload logs

    @staticmethod
    def save_upload_log(filename, file_size=None, status="Voltooid", gebruiker_id=None):
        # Slaat één upload op in de database

        try:
            # Maak een nieuw logje
            upload_log = UploadLog(
                filename=filename,                 # Naam van het bestand
                file_size=file_size,               # Grootte van het bestand
                upload_datetime=datetime.utcnow(), # Tijd van upload
                status=status,                     # Gelukt of mislukt
                gebruiker_id=gebruiker_id          # Wie uploadde
            )

            # Opslaan in database
            db.session.add(upload_log)
            db.session.commit()
            return True

        except Exception as e:
            # Als er iets fout gaat
            current_app.logger.error(f"Fout bij opslaan upload log: {e}")
            db.session.rollback()   # Alles terugdraaien
            return False

    @staticmethod
    def get_all_uploads():
        # Haalt alle uploads op, nieuwste eerst

        try:
            return UploadLog.query.order_by(
                UploadLog.upload_datetime.desc()
            ).all()
        except Exception as e:
            current_app.logger.error(f"Fout bij ophalen uploads: {e}")
            return []

    @staticmethod
    def get_upload_statistics():
        # Haalt simpele upload cijfers op

        try:
            # Totaal aantal uploads
            total_uploads = UploadLog.query.count()

            # Uploads van vandaag
            today = datetime.utcnow().date()
            today_uploads = UploadLog.query.filter(
                db.func.date(UploadLog.upload_datetime) == today
            ).count()

            # Uploads van deze week
            week_ago = datetime.utcnow() - timedelta(days=7)
            week_uploads = UploadLog.query.filter(
                UploadLog.upload_datetime >= week_ago
            ).count()

            return {
                "total_uploads": total_uploads,
                "today_uploads": today_uploads,
                "week_uploads": week_uploads
            }

        except Exception as e:
            # Als ophalen mislukt
            current_app.logger.error(f"Fout bij ophalen statistieken: {e}")
            return {
                "total_uploads": 0,
                "today_uploads": 0,
                "week_uploads": 0
            }

    @staticmethod
    def format_uploads_for_template(uploads):
        # Maakt uploads netjes voor de website

        formatted = []

        # Welke icoon bij welk bestand hoort
        icon_map = {
            '.pdf': '📄', '.doc': '📄', '.docx': '📄', '.txt': '📄',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️',
            '.mp4': '🎥', '.mp3': '🎵',
            '.zip': '📦',
            '.xls': '📊', '.xlsx': '📊', '.ppt': '📊', '.pptx': '📊'
        }

        for upload in uploads:
            # datum en tijd netjes maken
            date_str = upload.upload_datetime.strftime("%d %b %Y")
            time_str = upload.upload_datetime.strftime("%H:%M:%S")

            # Kijken of er GB, MB of KB moet worden weergeven
            size_bytes = upload.file_size or 0
            if size_bytes >= 1024**3:
                size_str = f"{round(size_bytes / (1024**3), 2)} GB"
            elif size_bytes >= 1024**2:
                size_str = f"{round(size_bytes / (1024**2), 2)} MB"
            elif size_bytes >= 1024:
                size_str = f"{round(size_bytes / 1024, 2)} KB"
            else:
                size_str = f"{size_bytes} B"

            # icoon bepalen op basis van extensie
            ext = os.path.splitext(upload.filename)[1].lower()
            icon = icon_map.get(ext, '📄')

            # Alles samen in een dict
            formatted.append({
                "filename": upload.filename,
                "date": date_str,
                "time": time_str,
                "size": size_str,
                "status": upload.status,
                "icon": icon
            })

        return formatted
