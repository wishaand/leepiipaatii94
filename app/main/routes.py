from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from . import bp
from app import db
from app.models import User, Betaling, Abonnement
from app.forms import LoginForm, RegisterForm, ContactForm, ChangePasswordForm, PasswordResetRequestForm, PasswordResetForm
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
            login_user(user, remember=form.remember_me.data)
            return redirect(url_for('main.betalingen_overzicht'))
        flash('Ongeldige gebruikersnaam of wachtwoord', 'error')
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


@bp.route("/contact", methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Hier kun je later de contact formulier data verwerken (bijv. email versturen, database opslaan)
        flash('Bedankt voor je bericht! We nemen zo snel mogelijk contact met je op.', 'success')
        return redirect(url_for('main.contact'))
    return render_template('contact.html', form=form)


@bp.route("/betalingen")
def betalingen_overzicht():
    betalingen = Betaling.query.order_by(Betaling.id.desc()).all()
    return render_template("betalingen_overzicht.html", betalingen=betalingen)


@bp.route("/wijzig-wachtwoord", methods=['GET', 'POST'])
@login_required
def wijzig_wachtwoord():
    """Wachtwoord wijzigen pagina"""
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Controleer of huidig wachtwoord klopt
        if not current_user.check_password(form.current_password.data):
            flash('Huidig wachtwoord is onjuist', 'error')
            return redirect(url_for('main.wijzig_wachtwoord'))
        
        # Stel nieuw wachtwoord in
        current_user.set_password(form.new_password.data)
        
        try:
            db.session.commit()
            flash('Je wachtwoord is succesvol gewijzigd!', 'success')
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Fout bij wachtwoord wijzigen: {e}")
            flash('Er is een fout opgetreden. Probeer het opnieuw.', 'error')
            return redirect(url_for('main.wijzig_wachtwoord'))
    
    return render_template('wijzig_wachtwoord.html', form=form)

@bp.route("/wachtwoord-vergeten", methods=['GET', 'POST'])
def wachtwoord_vergeten():
    """Vraag wachtwoord reset aan"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = PasswordResetRequestForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            # Genereer reset token
            token = user.generate_reset_token()
            
            try:
                db.session.commit()
                
                # TODO: Stuur email met reset link (nu alleen flash message)
                reset_url = url_for('main.reset_wachtwoord', token=token, _external=True)
                
                # In productie: verstuur email met reset_url
                # Voor nu: toon link in flash message (alleen voor development!)
                flash(f'Reset link (DEVELOPMENT ONLY): {reset_url}', 'info')
                flash('Als dit emailadres bestaat, is er een reset link verstuurd.', 'success')
                
                return redirect(url_for('main.login'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Fout bij reset token: {e}")
                flash('Er is een fout opgetreden. Probeer het opnieuw.', 'error')
        else:
            # Security: toon altijd succesbericht (ook als email niet bestaat)
            flash('Als dit emailadres bestaat, is er een reset link verstuurd.', 'success')
            return redirect(url_for('main.login'))
    
    return render_template('wachtwoord_vergeten.html', form=form)


@bp.route("/reset-wachtwoord/<token>", methods=['GET', 'POST'])
def reset_wachtwoord(token):
    """Reset wachtwoord met token"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Zoek gebruiker met deze token
    user = User.query.filter_by(reset_token=token).first()
    
    if not user or not user.verify_reset_token(token):
        flash('Ongeldige of verlopen reset link.', 'error')
        return redirect(url_for('main.login'))
    
    form = PasswordResetForm()
    
    if form.validate_on_submit():
        # Stel nieuw wachtwoord in
        user.set_password(form.password.data)
        user.clear_reset_token()
        
        try:
            db.session.commit()
            flash('Je wachtwoord is succesvol gereset! Je kunt nu inloggen.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Fout bij wachtwoord reset: {e}")
            flash('Er is een fout opgetreden. Probeer het opnieuw.', 'error')
    
    return render_template('reset_wachtwoord.html', form=form, token=token)
