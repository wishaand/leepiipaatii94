from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login

class User(UserMixin, db.Model):
    __tablename__ = 'gebruiker'
    
    gebruiker_id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    wachtwoord = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum('gebruiker', 'admin'), default='gebruiker')
    aanmaakdatum = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    registratie = db.relationship('Registration', backref='gebruiker', lazy=True)
    logins = db.relationship('Login', backref='gebruiker', lazy=True)
    
    def set_password(self, password):
        self.wachtwoord = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.wachtwoord, password)

class Registration(db.Model):
    __tablename__ = 'registratie'
    
    registratie_id = db.Column(db.Integer, primary_key=True)
    gebruiker_id = db.Column(db.Integer, db.ForeignKey('gebruiker.gebruiker_id'))
    verificatie_token = db.Column(db.String(255))
    status = db.Column(db.Enum('in_afwachting', 'bevestigd', 'afgewezen'), default='in_afwachting')
    registratie_datum = db.Column(db.DateTime, default=datetime.utcnow)

class Login(db.Model):
    __tablename__ = 'login'
    
    login_id = db.Column(db.Integer, primary_key=True)
    gebruiker_id = db.Column(db.Integer, db.ForeignKey('gebruiker.gebruiker_id'), nullable=False)
    login_tijd = db.Column(db.DateTime, default=datetime.utcnow)
    ip_adres = db.Column(db.String(45))
    succes = db.Column(db.Boolean, default=True)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))