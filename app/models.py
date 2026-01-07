from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import secrets
from datetime import datetime, timedelta


class User(UserMixin, db.Model):
    __tablename__ = "gebruiker"   

    gebruiker_id = db.Column(db.Integer, primary_key=True)  
    voornaam = db.Column(db.String(64), nullable=False)      
    achternaam = db.Column(db.String(64), nullable=False)   
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)   
    telefoon = db.Column(db.String(20))                     
    wachtwoord = db.Column(db.String(255), nullable=False)
    
    # Nieuw: Reset token velden
    reset_token = db.Column(db.String(100), unique=True, nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def set_password(self, password):
        self.wachtwoord = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.wachtwoord, password)

    def get_id(self):
        return str(self.gebruiker_id)
    
    def generate_reset_token(self):
        """Genereer een veilige reset token (geldig 1 uur)"""
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)
        return self.reset_token
    
    def verify_reset_token(self, token):
        """Controleer of token geldig is en niet verlopen"""
        if self.reset_token != token:
            return False
        if self.reset_token_expiry < datetime.utcnow():
            return False
        return True
    
    def clear_reset_token(self):
        """Verwijder reset token na gebruik"""
        self.reset_token = None
        self.reset_token_expiry = None



# Abonnement model 

class Abonnement(db.Model):
    __tablename__ = "abonnement"  # Naam van de tabel

    abonnement_id = db.Column(db.Integer, primary_key=True)  
    naam = db.Column(db.String(120), nullable=False)         
    prijs = db.Column(db.Numeric(10, 2), nullable=False)     
    looptijd_maanden = db.Column(db.Integer, nullable=False, default=12)  
    actief = db.Column(db.Boolean, default=True)           

    # Relatie
    betalingen = db.relationship(
        "Betaling",
        back_populates="abonnement",
        cascade="all, delete-orphan",
        lazy="select"
    )



# Betaling model 

class Betaling(db.Model):
    __tablename__ = "betaling"  # Naam van de tabel

    id = db.Column(db.Integer, primary_key=True)   

    # Foreign key: koppelt een betaling aan een abonnement
    abonnement_id = db.Column(
        db.Integer,
        db.ForeignKey("abonnement.abonnement_id"),
        nullable=False
    )

    bedrag = db.Column(db.Numeric(10, 2), nullable=False)   
    status = db.Column(db.String(32), nullable=False, default="open")  
    betaald_op = db.Column(db.DateTime)   

    # Relatie terug naar het bijbehorende abonnement
    abonnement = db.relationship("Abonnement", back_populates="betalingen")



# Contact model 

class Contact(db.Model):
    __tablename__ = "contact"  

    id = db.Column(db.Integer, primary_key=True)  
    naam = db.Column(db.String(128), nullable=False)  
    email = db.Column(db.String(120), nullable=False, index=True)   
    telefoon = db.Column(db.String(20))   
    onderwerp = db.Column(db.String(150), nullable=False)   
    bericht = db.Column(db.Text, nullable=False)   
    created_at = db.Column(db.DateTime, default=db.func.now())  


class UploadLog(db.Model):
    __tablename__ = "upload_log"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    upload_datetime = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(50), default="Voltooid")
    gebruiker_id = db.Column(db.Integer, db.ForeignKey("gebruiker.gebruiker_id"))



# Flask-Login user loader
# Wordt gebruikt om een gebruiker uit de database te halen

@login.user_loader
def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None