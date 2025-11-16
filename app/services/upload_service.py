# upload_service.py
# Hoofdservice: coördineert alle andere services

from werkzeug.utils import secure_filename


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

    def upload_file(self, file):
        """Upload een bestand naar Nextcloud."""
        # Check of er een bestand is
        if not file or not file.filename:
            return False, "Geen bestand geselecteerd"
        
        # Maak bestandsnaam veilig
        filename = secure_filename(file.filename)
        if not filename:
            return False, "Ongeldige bestandsnaam"

        # Controleer bestandstype
        if not self.validator.is_allowed(filename):
            return False, "Bestandstype niet toegestaan"

        # Controleer grootte
        if not self.validator.is_not_too_large(file):
            return False, "Bestand is te groot"

        # Sla tijdelijk op
        temp_path = self.storage.save_temp(file, filename)

        try:
            # Lees bestand
            content = self.storage.load_bytes(temp_path)

            # Upload naar Nextcloud
            ok = self.nc.upload(filename, content)
            if ok:
                return True, f"{filename} geüpload"
            return False, "Upload mislukt"

        finally:
            # Ruim altijd op
            self.storage.delete(temp_path)
