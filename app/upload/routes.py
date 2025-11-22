from flask import render_template, request, redirect, url_for, flash, send_file
from app.upload import bp
import io

# Importeer alles vanuit services (via __init__.py)
from app.services import build_service


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
