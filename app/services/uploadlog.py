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
   