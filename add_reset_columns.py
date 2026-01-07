from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check eerst of kolommen al bestaan
        result = db.session.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'gebruiker' 
            AND COLUMN_NAME = 'reset_token'
        """))
        
        if result.scalar() == 0:
            db.session.execute(text("""
                ALTER TABLE gebruiker 
                ADD COLUMN reset_token VARCHAR(100) UNIQUE
            """))
            print("✅ reset_token kolom toegevoegd")
        else:
            print("ℹ️  reset_token kolom bestaat al")
        
        # Check reset_token_expiry
        result = db.session.execute(text("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'gebruiker' 
            AND COLUMN_NAME = 'reset_token_expiry'
        """))
        
        if result.scalar() == 0:
            db.session.execute(text("""
                ALTER TABLE gebruiker 
                ADD COLUMN reset_token_expiry DATETIME
            """))
            print("✅ reset_token_expiry kolom toegevoegd")
        else:
            print("ℹ️  reset_token_expiry kolom bestaat al")
        
        db.session.commit()
        print("✅ Database update succesvol!")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Fout: {e}")