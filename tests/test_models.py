import pytest
from app.models import User, load_user

def test_set_and_check_password():
    u = User()
    u.wachtwoord = ""
    u.set_password("s3cr3t")
    assert u.wachtwoord != "s3cr3t"
    assert u.check_password("s3cr3t") is True
    assert u.check_password("wrong") is False

def test_get_id_returns_string_of_gebruiker_id():
    u = User()
    u.gebruiker_id = 123
    assert u.get_id() == "123"
    assert isinstance(u.get_id(), str)

def test_load_user_uses_query_get(monkeypatch):
    u = User()
    u.gebruiker_id = 5

    class FakeQuery:
        @staticmethod
        def get(_id):
            return u if int(_id) == 5 else None

    monkeypatch.setattr(User, "query", FakeQuery)
    assert load_user("5") is u
    assert load_user("999") is None

def test_tablename_is_gebruiker():
    assert getattr(User, "__tablename__", None) == "gebruiker"