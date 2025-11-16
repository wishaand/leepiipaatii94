from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")

    from app.upload import bp as upload_bp
    app.register_blueprint(upload_bp, url_prefix="/")

    return app
