from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from app.upload import bp
from app.file_upload_service import FileUploadService
import io

@bp.route("/")
def index():
    """Upload page"""
    # Load files from Nextcloud
    files = FileUploadService.list_files()
    return render_template("upload.html", files=files)

@bp.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        flash('Geen bestand geselecteerd')
        return redirect(url_for('upload.index'))
    
    file = request.files['file']
    
    if not file or file.filename == '':
        flash('Geen bestand geselecteerd')
        return redirect(url_for('upload.index'))
    
    # Use FileUploadService to upload to Nextcloud
    success, message = FileUploadService.upload_file(file)
    flash(message)
    
    return redirect(url_for('upload.index'))


@bp.route("/download/<filename>")
def download_file(filename):
    """Download file from Nextcloud"""
    file_content = FileUploadService.download_file(filename)
    
    if file_content:
        return send_file(
            io.BytesIO(file_content),
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
    else:
        flash(f'Bestand {filename} niet gevonden', 'error')
        return redirect(url_for('upload.index'))


