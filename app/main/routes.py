<<<<<<< Updated upstream
from flask import render_template, request, redirect, url_for

from app.main import bp


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/over-mij")
def about_me():
    return render_template("zelfportret.html")


@bp.route("/login")
def login():
    return render_template("login.html")


@bp.route("/upload")
def upload():
    return render_template("upload.html")


@bp.route("/registreer", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        first_name = request.form.get("first_name")
        last_name = request.form.get("last_name") 
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        # TODO: add validation and database storage logic here
        return redirect(url_for("main.index"))
    return render_template("registreer.html")
