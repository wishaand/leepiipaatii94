from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.main import bp
from app import db
from app.models import User

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
            flash("Ingelogd", "success")
            return redirect(url_for("main.index"))
        flash("Ongeldige inloggegevens", "danger")
    return render_template("login.html")


@bp.route("/registreer", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    if request.method == "POST":
        email = request.form.get("email", "").lower()
        if User.query.filter_by(email=email).first():
            flash("E-mail bestaat al", "warning")
            return redirect(url_for("main.register"))
        user = User(
            email=email,
            first_name=request.form.get("first_name"),
            last_name=request.form.get("last_name"),
        )
        user.set_password(request.form.get("password"))
        db.session.add(user)
        db.session.commit()
        flash("Account aangemaakt. Log in.", "success")
        return redirect(url_for("main.login"))
    return render_template("registreer.html")