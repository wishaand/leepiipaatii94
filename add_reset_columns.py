from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Voeg reset_token kolom toe
        db.session.execute(text("""
            ALTER TABLE gebruiker 
            ADD COLUMN IF NOT EXISTS reset_token VARCHAR(100) UNIQUE
        """))
        
        # Voeg reset_token_expiry kolom toe
        db.session.execute(text("""
            ALTER TABLE gebruiker 
            ADD COLUMN IF NOT EXISTS reset_token_expiry DATETIME
        """))
        
        db.session.commit()
        print("✅ Reset token kolommen succesvol toegevoegd!")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Fout: {e}")