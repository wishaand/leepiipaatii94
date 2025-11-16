from flask import render_template, request, redirect, url_for, flash, send_file
from app.upload import bp
from app.file_upload_service import FileUploadService
import io

@bp.route("/")
def index():
    service = FileUploadService()
    files = service.list_files()
    print(f"DEBUG: Found {len(files)} files: {files}")  # Debug output
    return render_template("upload.html", files=files)


@bp.route("/upload", methods=["POST"])
def upload_file():
    file = request.files.get("file")

    service = FileUploadService()
    success, message = service.upload_file(file)

    flash(message)
    return redirect(url_for("upload.index"))


@bp.route("/download/<filename>")
def download_file(filename):
    service = FileUploadService()
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
