from app import create_app, db
from app.models import Abonnement, Betaling

app = create_app()
with app.app_context():
    db.session.rollback()
    
    ab = Abonnement(
        naam="Premium Plan",
        prijs=29.99,
        looptijd_maanden=12,
        actief=True
    )
    db.session.add(ab)
    db.session.commit()
    print(f"✅ Abonnement: {ab.naam} (ID: {ab.abonnement_id})")

    b = Betaling(
        abonnement_id=ab.abonnement_id,
        bedrag=29.99,
        status="betaald"
    )
    db.session.add(b)
    db.session.commit()
    
    abonnement = Abonnement.query.first()
    print(f"📋 {abonnement.naam}:")
    for betaling in abonnement.betalingen:
        print(f"  - €{betaling.bedrag} ({betaling.status})")