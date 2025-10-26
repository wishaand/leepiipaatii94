from flask import render_template

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

