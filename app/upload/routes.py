import os
from flask import render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from app.upload import bp

# Upload configuration
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', 'mp4', 'mp3', 'wav'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route("/")
def index():
    """Upload page"""
    return render_template("upload.html")

@bp.route("/upload", methods=["POST"])
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        flash('Geen bestand geselecteerd')
        return redirect(url_for('upload.index'))
    
    files = request.files.getlist('file')
    
    if not files or all(file.filename == '' for file in files):
        flash('Geen bestand geselecteerd')
        return redirect(url_for('upload.index'))
    
    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Create upload directory if it doesn't exist
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            
            # Save file
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            uploaded_files.append(filename)
        else:
            flash(f'Bestandstype niet toegestaan: {file.filename}')
    
    if uploaded_files:
        flash(f'Bestanden succesvol geüpload: {", ".join(uploaded_files)}')
    
    return redirect(url_for('upload.index'))


