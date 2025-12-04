from app import create_app, db
from app.models import Contact

app = create_app()

with app.app_context():
    # Test: nieuwe contact aanmaken
    contact = Contact(
        naam="Jan Jansen",
        email="jan@example.com",
        telefoon="06-12345678",
        onderwerp="Vraag over abonnement",
        bericht="Hoe kan ik mijn abonnement upgraden?"
    )
    
    db.session.add(contact)
    db.session.commit()
    
    print(f"✅ Contact aangemaakt (ID: {contact.id})")
    print(f"   Naam: {contact.naam}")
    print(f"   Email: {contact.email}")
    print(f"   Bericht: {contact.bericht}")
    
    # Test: contact ophalen
    retrieved = Contact.query.filter_by(email="jan@example.com").first()
    print(f"\n✅ Contact opgehaald: {retrieved.naam}")
    
    # Test: alle contacten
    all_contacts = Contact.query.all()
    print(f"\n✅ Totaal contacten in database: {len(all_contacts)}")