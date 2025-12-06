from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from . import bp
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm, ContactForm
from sqlalchemy.exc import OperationalError

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/over-mij')
def about_me():
    return render_template('zelfportret.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Ongeldige inloggegevens')
    return render_template('login.html', form=form)

@bp.route('/registreer', methods=['GET', 'POST'])
def registreer():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            voornaam=form.voornaam.data,
            achternaam=form.achternaam.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        try:
            db.session.commit()
        except OperationalError as e:
            db.session.rollback()
            current_app.logger.error("DB OperationalError bij register: %s", e)
            error_msg = str(e)
            # Geef meer details in development mode
            if current_app.config.get('DEBUG'):
                flash(f"Database fout: {error_msg}", "error")
            else:
                flash("Er is een verbindingsfout met de database. Controleer je database configuratie.", "error")
            return redirect(url_for('main.registreer'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error("Onverwachte fout bij register: %s", e)
            flash(f"Er is een fout opgetreden: {str(e)}", "error")
            return redirect(url_for('main.registreer'))
        flash('Account aangemaakt! Je kunt nu inloggen.')
        return redirect(url_for('main.login'))
    return render_template('registreer.html', form=form)

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        file = request.files.get("file")
        if not file:
            flash("Geen bestand geselecteerd", "warning")
            return redirect(url_for("main.upload"))
        flash("Bestand ontvangen (debug)", "success")
        return redirect(url_for("main.index"))
    return render_template("upload.html")


@bp.route("/search")
def search():
    """Zoek functie voor bestanden in Nextcloud."""
    from app.services.service_factory import build_service
    
    # Haal zoekterm op uit URL parameter
    query = request.args.get('q', '').strip()
    search_results = []
    all_files = []
    
    try:
        # Haal alle bestanden op uit Nextcloud
        service = build_service()
        all_files = service.list_files()
        
        # Filter bestanden op basis van zoekterm
        if query:
            query_lower = query.lower()
            search_results = [f for f in all_files if query_lower in f.lower()]
        else:
            # Als er geen zoekterm is, toon alle bestanden
            search_results = all_files
            
    except Exception as e:
        current_app.logger.error(f"Fout bij zoeken: {e}")
        flash(f"Fout bij het ophalen van bestanden: {str(e)}", "error")
    
    return render_template("search.html", 
                         query=query, 
                         results=search_results, 
                         total_files=len(all_files))


@bp.route("/favorieten")
def favorites():
    return render_template("favorites.html")


@bp.route("/opslag")
def opslag():
    """Opslag pagina - toont opslag informatie van Nextcloud"""
    from app.services.nextcloud_client import NextcloudClient
    import os
    from datetime import datetime
    
    # Default waarden voor als Nextcloud niet bereikbaar is
    storage_total = 0
    storage_used = 0
    storage_available = 0
    storage_percentage = 0
    storage_by_type = []
    largest_files = []
    
    try:
        # Maak Nextcloud client aan
        server_url = current_app.config.get("NEXTCLOUD_SERVER_URL")
        username = current_app.config.get("NEXTCLOUD_USERNAME")
        password = current_app.config.get("NEXTCLOUD_PASSWORD")
        folder = current_app.config.get("NEXTCLOUD_FOLDER")
        
        if not all([server_url, username, password, folder]):
            flash("Nextcloud configuratie ontbreekt", "error")
            return render_template("opslag.html",
                                 storage_total=storage_total,
                                 storage_used=storage_used,
                                 storage_available=storage_available,
                                 storage_percentage=storage_percentage,
                                 storage_by_type=storage_by_type,
                                 largest_files=largest_files)
        
        nc = NextcloudClient(server_url, username, password, folder)
        
        # Haal quota informatie op
        quota = nc.get_storage_quota()
        if quota:
            # Converteer bytes naar GB
            storage_used = round(quota["used"] / (1024**3), 2) if quota["used"] else 0
            if quota["total"]:
                storage_total = round(quota["total"] / (1024**3), 2)
                storage_available = round((quota["total"] - quota["used"]) / (1024**3), 2) if quota["used"] else storage_total
            elif quota["available"] and quota["available"] >= 0:
                storage_available = round(quota["available"] / (1024**3), 2)
                storage_total = storage_used + storage_available
            
            if storage_total > 0:
                storage_percentage = round((storage_used / storage_total) * 100, 1)
        
        # Haal bestanden op met details
        files = nc.get_files_with_details()
        
        # Groepeer bestanden per type
        type_sizes = {
            "Documenten": 0,
            "Afbeeldingen": 0,
            "Video's": 0,
            "Audio": 0,
            "Overig": 0
        }
        
        type_icons = {
            "Documenten": "📄",
            "Afbeeldingen": "🖼️",
            "Video's": "🎥",
            "Audio": "🎵",
            "Overig": "📦"
        }
        
        document_exts = {'.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.csv', '.ppt', '.pptx'}
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'}
        video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm'}
        audio_exts = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
        
        for file_info in files:
            ext = os.path.splitext(file_info["name"])[1].lower()
            size_gb = file_info["size"] / (1024**3)
            
            if ext in document_exts:
                type_sizes["Documenten"] += size_gb
            elif ext in image_exts:
                type_sizes["Afbeeldingen"] += size_gb
            elif ext in video_exts:
                type_sizes["Video's"] += size_gb
            elif ext in audio_exts:
                type_sizes["Audio"] += size_gb
            else:
                type_sizes["Overig"] += size_gb
        
        # Maak storage_by_type lijst
        total_type_size = sum(type_sizes.values())
        storage_by_type = []
        for type_name, size in type_sizes.items():
            if size > 0:
                percentage = round((size / total_type_size) * 100, 1) if total_type_size > 0 else 0
                storage_by_type.append({
                    "name": type_name,
                    "size": round(size, 2),
                    "icon": type_icons[type_name],
                    "percentage": percentage
                })
        
        # Sorteer bestanden op grootte en neem de 5 grootste
        files_sorted = sorted(files, key=lambda x: x["size"], reverse=True)[:5]
        largest_files = []
        
        for file_info in files_sorted:
            size_bytes = file_info["size"]
            if size_bytes >= 1024**3:  # GB
                size_str = f"{round(size_bytes / (1024**3), 2)} GB"
            elif size_bytes >= 1024**2:  # MB
                size_str = f"{round(size_bytes / (1024**2), 2)} MB"
            elif size_bytes >= 1024:  # KB
                size_str = f"{round(size_bytes / 1024, 2)} KB"
            else:
                size_str = f"{size_bytes} B"
            
            # Format datum
            date_str = "Onbekend"
            if file_info["date"]:
                try:
                    # Parse RFC 1123 format (bijv. "Wed, 15 Jan 2025 10:30:00 GMT")
                    dt = datetime.strptime(file_info["date"], "%a, %d %b %Y %H:%M:%S %Z")
                    date_str = dt.strftime("%d %b %Y")
                except:
                    try:
                        # Probeer alternatief formaat
                        dt = datetime.fromisoformat(file_info["date"].replace('Z', '+00:00'))
                        date_str = dt.strftime("%d %b %Y")
                    except:
                        date_str = file_info["date"][:10] if len(file_info["date"]) >= 10 else "Onbekend"
            
            largest_files.append({
                "name": file_info["name"],
                "size": size_str,
                "date": date_str,
                "icon": nc.get_file_icon(file_info["name"])
            })
        
    except Exception as e:
        current_app.logger.error(f"Fout bij ophalen opslag informatie: {e}")
        flash(f"Fout bij het ophalen van opslag informatie: {str(e)}", "error")
    
    return render_template("opslag.html",
                         storage_total=storage_total,
                         storage_used=storage_used,
                         storage_available=storage_available,
                         storage_percentage=storage_percentage,
                         storage_by_type=storage_by_type,
                         largest_files=largest_files)


@bp.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Hier kun je later de contact formulier data verwerken (bijv. email versturen, database opslaan)
        flash('Bedankt voor je bericht! We nemen zo snel mogelijk contact met je op.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html', form=form)
