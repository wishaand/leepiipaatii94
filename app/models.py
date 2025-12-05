from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class User(UserMixin, db.Model):
    __tablename__ = "gebruiker"

    gebruiker_id = db.Column(db.Integer, primary_key=True)
    voornaam = db.Column(db.String(64), nullable=False)
    achternaam = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    telefoon = db.Column(db.String(20))
    wachtwoord = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        self.wachtwoord = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.wachtwoord, password)

    def get_id(self):
        return str(self.gebruiker_id)


class Abonnement(db.Model):
    __tablename__ = "abonnement"

    abonnement_id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(120), nullable=False)
    prijs = db.Column(db.Numeric(10, 2), nullable=False)
    looptijd_maanden = db.Column(db.Integer, nullable=False, default=12)
    actief = db.Column(db.Boolean, default=True)

    betalingen = db.relationship(
        "Betaling",
        back_populates="abonnement",
        cascade="all, delete-orphan",
        lazy="select"
    )


class Betaling(db.Model):
    __tablename__ = "betaling"

    id = db.Column(db.Integer, primary_key=True)
    abonnement_id = db.Column(db.Integer, db.ForeignKey("abonnement.abonnement_id"), nullable=False)
    bedrag = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="open")
    betaald_op = db.Column(db.DateTime)

    abonnement = db.relationship("Abonnement", back_populates="betalingen")


class Contact(db.Model):
    __tablename__ = "contact"

    id = db.Column(db.Integer, primary_key=True)
    naam = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    telefoon = db.Column(db.String(20))
    onderwerp = db.Column(db.String(150), nullable=False)
    bericht = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))