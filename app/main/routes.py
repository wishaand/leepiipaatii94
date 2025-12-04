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
    """Opslag pagina - toont opslag informatie (nu met voorbeeld data, later Nextcloud)"""
    # Voorbeeld opslag data
    storage_total = 100  # GB
    storage_used = 42.5  # GB
    storage_available = storage_total - storage_used
    storage_percentage = round((storage_used / storage_total) * 100, 1)
    
    # Opslag per bestandstype (voorbeeld)
    storage_by_type = [
        {"name": "Documenten", "size": 15.2, "icon": "📄", "percentage": 35.8},
        {"name": "Afbeeldingen", "size": 18.5, "icon": "🖼️", "percentage": 43.5},
        {"name": "Video's", "size": 5.8, "icon": "🎥", "percentage": 13.6},
        {"name": "Audio", "size": 2.1, "icon": "🎵", "percentage": 4.9},
        {"name": "Overig", "size": 0.9, "icon": "📦", "percentage": 2.1}
    ]
    
    # Grootste bestanden (voorbeeld)
    largest_files = [
        {"name": "project_presentatie.pdf", "size": "2.4 GB", "date": "15 Jan 2025", "icon": "📄"},
        {"name": "team_foto_2024.jpg", "size": "1.8 GB", "date": "10 Jan 2025", "icon": "🖼️"},
        {"name": "video_demo.mp4", "size": "1.2 GB", "date": "8 Jan 2025", "icon": "🎥"},
        {"name": "jaarverslag_2024.pdf", "size": "850 MB", "date": "5 Jan 2025", "icon": "📄"},
        {"name": "muziek_collectie.zip", "size": "650 MB", "date": "3 Jan 2025", "icon": "🎵"}
    ]
    
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
