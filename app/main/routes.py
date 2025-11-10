from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from . import bp
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm
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
            flash("Er is een verbindingsfout met de database. Probeer het opnieuw.")
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
    return render_template("search.html")
@bp.route('/contact')
def contact():
    return render_template('contact.html')
