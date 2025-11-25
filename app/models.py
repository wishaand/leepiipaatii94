from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = "gebruiker"

    gebruiker_id = db.Column(db.Integer, primary_key=True)
    voornaam = db.Column(db.String(64))
    achternaam = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, index=True)
    telefoon = db.Column(db.String(20))
    wachtwoord = db.Column(db.String(128))

    def set_password(self, password):
        self.wachtwoord = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.wachtwoord, password)

    def get_id(self):
        return str(self.gebruiker_id)

@login.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None