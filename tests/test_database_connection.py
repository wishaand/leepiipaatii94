import pytest
from app import create_app, db
from app.models import User
from sqlalchemy import text, inspect


@pytest.fixture
def app():
    """Test-app met schone database per test."""
    app = create_app()
    with app.app_context():
        # FK checks uit, alle tabellen droppen
        db.session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        inspector = inspect(db.engine)
        for table_name in reversed(inspector.get_table_names()):
            db.session.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
        db.session.commit()
        db.session.execute(text("SET FOREIGN_KEY_CHECKS=1"))

        # Schone tabellen aanmaken
        db.create_all()
        yield app

        # Opruimen na test
        db.session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for table_name in reversed(inspector.get_table_names()):
            db.session.execute(text(f"DROP TABLE IF EXISTS `{table_name}`"))
        db.session.commit()
        db.session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        db.session.remove()


def test_database_connection(app):
    """Check of de database bereikbaar is."""
    with app.app_context():
        result = db.session.execute(db.text("SELECT 1"))
        assert result.scalar() == 1


def test_create_user(app):
    """Check of een gebruiker kan worden opgeslagen."""
    with app.app_context():
        user = User(voornaam="Jan", achternaam="Jansen", email="jan@example.com")
        user.set_password("secure123")
        db.session.add(user)
        db.session.commit()
        assert user.gebruiker_id is not None


def test_retrieve_user(app):
    """Check of een gebruiker kan worden opgehaald."""
    with app.app_context():
        user = User(voornaam="Maria", achternaam="Meijer", email="maria@example.com")
        user.set_password("password456")
        db.session.add(user)
        db.session.commit()

        retrieved = User.query.filter_by(email="maria@example.com").first()
        assert retrieved is not None
        assert retrieved.voornaam == "Maria"
        assert retrieved.check_password("password456")

#pytest tests/test_database_connection.py -v  