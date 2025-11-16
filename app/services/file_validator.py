# file_validator.py
# Controleert of bestanden mogen: type en grootte

import os


class FileValidator:
    """Controleert bestandstype en grootte."""

    def __init__(self, allowed_extensions, max_size):
        """Sla regels op."""
        self.allowed_extensions = allowed_extensions  # Toegestane bestandstypen
        self.max_size = max_size  # Maximale grootte in bytes

    def is_allowed(self, filename):
        """Check of bestandstype is toegestaan."""
        return (
            '.' in filename and 
            filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
        )

    def is_not_too_large(self, file):
        """Check of bestand niet te groot is."""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        return size <= self.max_size
