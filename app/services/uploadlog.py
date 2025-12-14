# upload_log_service.py
# Beheert alle upload log functionaliteit

from app import db
from app.models import UploadLog
from datetime import datetime, timedelta
from flask import current_app
import os


class UploadLogService:
    """Service voor upload log functionaliteit."""
    
    @staticmethod
    def save_upload_log(filename, file_size=None, status="Voltooid", gebruiker_id=None):
        """
        Sla een upload log op in de database.
        
        Args:
            filename: Naam van het geüploade bestand
            file_size: Grootte van het bestand in bytes (optioneel)
            status: Status van de upload (default: "Voltooid")
            gebruiker_id: ID van de gebruiker die upload deed (optioneel)
        
        Returns:
            True als succesvol, False als mislukt
        """
        try:
            upload_log = UploadLog(
                filename=filename,
                file_size=file_size,
                upload_datetime=datetime.utcnow(),
                status=status,
                gebruiker_id=gebruiker_id
            )
            
            db.session.add(upload_log)
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Fout bij opslaan upload log: {e}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_all_uploads():
        """
        Haal alle uploads op, gesorteerd op nieuwste eerst.
        
        Returns:
            List van UploadLog objecten
        """
        try:
            return UploadLog.query.order_by(UploadLog.upload_datetime.desc()).all()
        except Exception as e:
            current_app.logger.error(f"Fout bij ophalen uploads: {e}")
            return []
    
    @staticmethod
    def get_upload_statistics():
        """
        Haal statistieken op over uploads.
        
        Returns:
            Dict met total_uploads, today_uploads, week_uploads
        """
        try:
            total_uploads = UploadLog.query.count()
            
            # Vandaag
            today = datetime.utcnow().date()
            today_uploads = UploadLog.query.filter(
                db.func.date(UploadLog.upload_datetime) == today
            ).count()
            
            # Deze week
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
            current_app.logger.error(f"Fout bij ophalen statistieken: {e}")
            return {
                "total_uploads": 0,
                "today_uploads": 0,
                "week_uploads": 0
            }

    @staticmethod
    def format_uploads_for_template(uploads):
        """
        Formatteer uploads voor gebruik in templates.
        
        Args:
            uploads: List van UploadLog objecten
        
        Returns:
            List van dicts met geformatteerde data
        """
        formatted = []
        
        # Icoon mapping
        icon_map = {
            '.pdf': '📄', '.doc': '📄', '.docx': '📄', '.txt': '📄', '.rtf': '📄',
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.bmp': '🖼️', '.svg': '🖼️',
            '.mp4': '🎥', '.avi': '🎥', '.mov': '🎥', '.mkv': '🎥', '.wmv': '🎥',
            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.aac': '🎵', '.ogg': '🎵',
            '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦', '.gz': '📦',
            '.xls': '📊', '.xlsx': '📊', '.csv': '📊',
            '.ppt': '📊', '.pptx': '📊'
        }
        
        for upload in uploads:
            # Format datum en tijd
            date_str = upload.upload_datetime.strftime("%d %b %Y")
            time_str = upload.upload_datetime.strftime("%H:%M:%S")
            
            # Format grootte
            size_bytes = upload.file_size or 0
            if size_bytes >= 1024**3:  # GB
                size_str = f"{round(size_bytes / (1024**3), 2)} GB"
            elif size_bytes >= 1024**2:  # MB
                size_str = f"{round(size_bytes / (1024**2), 2)} MB"
            elif size_bytes >= 1024:  # KB
                size_str = f"{round(size_bytes / 1024, 2)} KB"
            else:
                size_str = f"{size_bytes} B"
            
            # Bepaal icoon
            ext = os.path.splitext(upload.filename)[1].lower()
            icon = icon_map.get(ext, '📄')
            
            formatted.append({
                "filename": upload.filename,
                "date": date_str,
                "time": time_str,
                "size": size_str,
                "status": upload.status,
                "icon": icon
            })
        
        return formatted
