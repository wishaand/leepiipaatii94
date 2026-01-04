# upload_service.py
# voert alle andere functies uit om de functie uploaden/downloaden uit te kunnen voeren

from werkzeug.utils import secure_filename
from app.services.upload_log_service import UploadLogService


class FileUploadService:
    """Hoofdservice die alle andere services combineert."""

    def __init__(self, nextcloud_client, validator, storage):
        """Sla alle helpers op."""
        self.nc = nextcloud_client  # Praat met Nextcloud
        self.validator = validator  # Checkt of bestanden mogen
        self.storage = storage  # Bewaart bestanden tijdelijk

    def list_files(self):
        """Haal lijst van bestanden op van Nextcloud."""
        return self.nc.list_files()

    def download_file(self, filename):
        """Download een bestand van Nextcloud."""
        return self.nc.download(filename)

    def upload_file(self, file, gebruiker_id=None):
        if not file or not file.filename:
            return False, "Geen bestand geselecteerd"

        filename = secure_filename(file.filename)
        if not filename:
            return False, "Ongeldige bestandsnaam"

        if not self.validator.is_allowed(filename):
            return False, "Bestandstype niet toegestaan"

        if not self.validator.is_not_too_large(file):
            return False, "Bestand is te groot"

        temp_path = self.storage.save_temp(file, filename)

        try:
            content = self.storage.load_bytes(temp_path)
            file_size = len(content)

            ok = self.nc.upload(filename, content)

            if ok:
                # ✅ LOG SUCCES
                UploadLogService.save_upload_log(
                    filename=filename,
                    file_size=file_size,
                    status="Voltooid",
                    gebruiker_id=gebruiker_id
                )
                return True, f"{filename} geüpload"

            else:
                # ❌ LOG FOUT
                UploadLogService.save_upload_log(
                    filename=filename,
                    file_size=file_size,
                    status="Mislukt",
                    gebruiker_id=gebruiker_id
                )
                return False, "Upload mislukt"

        finally:
            self.storage.delete(temp_path)
