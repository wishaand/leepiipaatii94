from flask import render_template, request, redirect, url_for, flash, send_file, current_app
from app.upload import bp
import io

# Importeer alle nieuwe services
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


@bp.route("/")
def index():
    service = build_service()
    files = service.list_files()

    print(f"DEBUG: Found {len(files)} files: {files}")

    return render_template("upload.html", files=files)


@bp.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")

    service = build_service()
    success, message = service.upload_file(file)

    flash(message)
    return redirect(url_for("upload.index"))


@bp.route("/download/<filename>")
def download_file(filename):
    service = build_service()
    content = service.download_file(filename)

    if content:
        return send_file(
            io.BytesIO(content),
            as_attachment=True,
            download_name=filename,
            mimetype="application/octet-stream"
        )

    flash("Bestand niet gevonden")
    return redirect(url_for("upload.index"))
