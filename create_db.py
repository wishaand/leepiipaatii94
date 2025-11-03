import os
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

user = os.getenv("DB_USER")
pw = os.getenv("DB_PASSWORD", "")
host = os.getenv("DB_HOST", "localhost")
port = os.getenv("DB_PORT", "3306")
dbname = os.getenv("DB_NAME")

if not all([user, host, port, dbname]):
    raise SystemExit("Controleer DB_USER/DB_HOST/DB_PORT/DB_NAME in .env")

uri = f"mysql+pymysql://{user}:{quote_plus(pw)}@{host}:{port}/"
engine = create_engine(uri, echo=False)

with engine.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"))
    print("Database aangemaakt of bestaat al:", dbname)

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.main import bp
from app import db
from app.models import User
    
# Database-setup is verplaatst naar create_db.py — NIET uitvoeren tijdens module import
    
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
        if user and user.check_password(password):
            login_user(user)
            flash("Je bent succesvol ingelogd", "success")
            return redirect(url_for("main.index"))
        flash("Ongeldige email of wachtwoord", "error")
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
        user = User(
            voornaam=request.form.get("first_name"),
            achternaam=request.form.get("last_name"),
            email=email,
            telefoon=request.form.get("phone")
        )
        user.set_password(request.form.get("password"))
        try:
            db.session.add(user)
            db.session.commit()
            flash("Account succesvol aangemaakt. Je kunt nu inloggen.", "success")
            return redirect(url_for("main.login"))
        except Exception:
            db.session.rollback()
            flash("Er is een fout opgetreden. Probeer het opnieuw.", "error")
            return redirect(url_for("main.register"))
    return render_template("registreer.html")
    
@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Je bent uitgelogd", "info")
    return redirect(url_for("main.index"))
    
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