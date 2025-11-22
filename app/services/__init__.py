# services/__init__.py
# Exporteert alle services zodat je ze kunt importeren via: from app.services import ...

# Export alle service classes
from app.services.upload_service import FileUploadService
from app.services.nextcloud_client import NextcloudClient
from app.services.file_validator import FileValidator
from app.services.temp_storage import TempStorage

# Export de factory functie
from app.services.service_factory import build_service

# Maak alles beschikbaar voor import
__all__ = [
    'FileUploadService',
    'NextcloudClient',
    'FileValidator',
    'TempStorage',
    'build_service'
]
