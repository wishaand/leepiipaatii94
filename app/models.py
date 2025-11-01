from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    __tablename__ = 'gebruiker'
    
    gebruiker_id = db.Column(db.Integer, primary_key=True)
    voornaam = db.Column(db.String(100))
    achternaam = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefoon = db.Column(db.String(20))
    wachtwoord = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.wachtwoord = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.wachtwoord, password)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))