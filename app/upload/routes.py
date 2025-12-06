from flask import render_template, request, redirect, url_for, flash, send_file
from app.upload import bp
import io

# Importeer alles vanuit services (via __init__.py)
from app.services import build_service


@bp.route("/")
def index():
    try:
        service = build_service()
        files = service.list_files()

        print(f"DEBUG: Found {len(files)} files: {files}")

        return render_template("upload.html", files=files)
    except Exception as e:
        print(f"ERROR in upload.index: {e}")
        flash(f"Fout bij het laden van bestanden: {str(e)}", "error")
        return render_template("upload.html", files=[])


@bp.route("/downloads")
def downloads():
    """Download pagina - toont alle beschikbare bestanden."""
    try:
        service = build_service()
        files = service.list_files()

        print(f"DEBUG: Download page - Found {len(files)} files: {files}")

        return render_template("download.html", files=files)
    except Exception as e:
        print(f"ERROR in upload.downloads: {e}")
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
    # Placeholder data - kan later worden vervangen met echte data
    uploads = []
    total_uploads = 0
    today_uploads = 0
    week_uploads = 0
    
    return render_template("uploadlog.html",
                         uploads=uploads,
                         total_uploads=total_uploads,
                         today_uploads=today_uploads,
                         week_uploads=week_uploads)
