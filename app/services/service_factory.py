# service_factory.py
# Factory die FileUploadService objecten maakt met alle dependencies

from flask import current_app
from app.services.upload_service import FileUploadService
from app.services.nextcloud_client import NextcloudClient
from app.services.file_validator import FileValidator
from app.services.temp_storage import TempStorage


def build_service():
    """Maakt een volledig FileUploadService object aan met alle dependencies."""
    
    nc = NextcloudClient(
        server_url=current_app.config["NEXTCLOUD_SERVER_URL"],
        username=current_app.config["NEXTCLOUD_USERNAME"],
        password=current_app.config["NEXTCLOUD_PASSWORD"],
        folder=current_app.config["NEXTCLOUD_FOLDER"]
    )

    validator = FileValidator(
        allowed_extensions={
            'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx',
            'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'mp4', 'mp3', 'wav'
        },
        max_size=100 * 1024 * 1024  # 100 MB
    )

    storage = TempStorage("app/static/uploads")

    return FileUploadService(nc, validator, storage)

