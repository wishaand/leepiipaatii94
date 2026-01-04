from flask import render_template, request, redirect, url_for, flash, send_file
from app.upload import bp
import io

# Bestand-services (opslag)
from app.services import build_service

# Upload log service (database)
from app.services import UploadLogService


@bp.route("/")
def index():
    try:
        service = build_service()
        files = service.list_files()

        return render_template("upload.html", files=files)
    except Exception as e:
        flash(f"Fout bij het laden van bestanden: {str(e)}", "error")
        return render_template("upload.html", files=[])


@bp.route("/downloads")
def downloads():
    """Download pagina - toont alle beschikbare bestanden."""
    try:
        service = build_service()
        files = service.list_files()

        return render_template("download.html", files=files)
    except Exception as e:
        flash(f"Fout bij het laden van bestanden: {str(e)}", "error")
        return render_template("download.html", files=[])


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


@bp.route("/uploadlog")
def uploadlog():
    """Upload log pagina - toont alle upload tijden en datums"""

    # 1. Data ophalen uit database
    uploads = UploadLogService.get_all_uploads()

    # 2. Statistieken ophalen
    stats = UploadLogService.get_upload_statistics()

    # 3. Formatteren voor template
    formatted_uploads = UploadLogService.format_uploads_for_template(uploads)

    return render_template(
        "uploadlog.html",
        uploads=formatted_uploads,
        total_uploads=stats["total_uploads"],
        today_uploads=stats["today_uploads"],
        week_uploads=stats["week_uploads"]
    )
