from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.main import bp
from app import db
from app.models import User, Login, Registration
import secrets

@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/over-mij")
def about_me():
    return render_template("zelfportret.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
        
    if request.method == "POST":
        email = request.form.get("email", "").lower()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        
        # Create login record
        login_record = Login(
            gebruiker_id=user.gebruiker_id if user else None,
            ip_adres=request.remote_addr,
            succes=False
        )
        
        if user and user.check_password(password):
            login_user(user)
            login_record.succes = True
            db.session.add(login_record)
            db.session.commit()
            flash("Succesvol ingelogd", "success")
            return redirect(url_for("main.index"))
            
        db.session.add(login_record)
        db.session.commit()
        flash("Ongeldige inloggegevens", "danger")
        
    return render_template("login.html")


@bp.route("/registreer", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
        
    if request.method == "POST":
        email = request.form.get("email", "").lower()
        if User.query.filter_by(email=email).first():
            flash("Email bestaat al", "warning")
            return redirect(url_for("main.register"))
            
        # Create new user
        user = User(
            naam=f"{request.form.get('first_name')} {request.form.get('last_name')}",
            email=email,
            rol='gebruiker'
        )
        user.set_password(request.form.get("password"))
        db.session.add(user)
        
        # Create registration record
        registration = Registration(
            gebruiker_id=user.gebruiker_id,
            verificatie_token=secrets.token_urlsafe(32),
            status='in_afwachting'
        )
        db.session.add(registration)
        db.session.commit()
        
        flash("Account aangemaakt. Je kunt nu inloggen.", "success")
        return redirect(url_for("main.login"))
        
    return render_template("registreer.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Je bent uitgelogd", "info")
    return redirect(url_for("main.index"))