# temp_storage.py
# Bewaart bestanden tijdelijk lokaal

import os


class TempStorage:
    """Bewaart bestanden tijdelijk op de computer."""

    def __init__(self, folder):
        """Sla map op waar bestanden komen."""
        self.folder = folder

    def save_temp(self, file, filename):
        """Sla bestand tijdelijk op."""
        os.makedirs(self.folder, exist_ok=True)
        path = os.path.join(self.folder, filename)
        file.save(path)
        return path

    def load_bytes(self, path):
        """Lees bestand in als bytes."""
        with open(path, "rb") as f:
            return f.read()

    def delete(self, path):
        """Verwijder bestand."""
        if os.path.exists(path):
            os.remove(path)
