from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
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

def load_user(user_id):
    try:
        return User.query.get(int(user_id))
    except Exception:
        return None

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

import pytest

def test_set_and_check_password():
    # Create a user and set a password
    u = User()
    # Ensure no plain password stored initially
    u.wachtwoord = ""
    u.set_password("s3cr3t")
    # stored password should not be the plain string
    assert u.wachtwoord != "s3cr3t"
    # correct password should validate
    assert u.check_password("s3cr3t") is True
    # incorrect password should fail
    assert u.check_password("wrong") is False

def test_get_id_returns_string_of_gebruiker_id():
    u = User()
    u.gebruiker_id = 123
    assert u.get_id() == "123"
    # Also ensure Flask-Login compatibility: get_id returns a string
    assert isinstance(u.get_id(), str)

def test_load_user_uses_query_get(monkeypatch):
    # Create a dummy user instance and a fake query.get implementation
    u = User()
    u.gebruiker_id = 5

    class FakeQuery:
        @staticmethod
        def get(_id):
            return u if int(_id) == 5 else None

    # Monkeypatch the User.query attribute to avoid DB access
    monkeypatch.setattr(User, "query", FakeQuery)

    # load_user expects a string id (Flask-Login passes string)
    assert load_user("5") is u
    assert load_user("999") is None

def test_tablename_is_gebruiker():
    assert getattr(User, "__tablename__", None) == "gebruiker"