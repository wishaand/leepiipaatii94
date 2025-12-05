"""Script om test-abonnement en betaling aan te maken in HBO-ICT Cloud"""

from app import create_app, db
from app.models import Abonnement, Betaling

app = create_app()

with app.app_context():
    # Controleer of test-abonnement al bestaat
    existing = Abonnement.query.filter_by(naam="Small Business").first()
    if existing:
        print(f"✅ Abonnement '{existing.naam}' bestaat al (ID: {existing.abonnement_id})")
    else:
        # Maak test-abonnementen aan
        abonnementen = [
            Abonnement(naam="Small Business", prijs=9.99, looptijd_maanden=12, actief=True),
            Abonnement(naam="Medium Business", prijs=29.99, looptijd_maanden=12, actief=True),
            Abonnement(naam="Enterprise", prijs=99.99, looptijd_maanden=12, actief=True),
        ]
        
        for ab in abonnementen:
            db.session.add(ab)
        
        db.session.commit()
        print(f"✅ {len(abonnementen)} test-abonnementen aangemaakt")
        
        # Voeg test-betalingen toe
        for ab in Abonnement.query.all():
            b = Betaling(
                abonnement_id=ab.abonnement_id,
                bedrag=ab.prijs,
                status="betaald"
            )
            db.session.add(b)
        
        db.session.commit()
        print(f"✅ Test-betalingen aangemaakt")

    # Toon alle abonnementen en hun betalingen
    print("\n📋 Overzicht van abonnementen en betalingen:")
    for ab in Abonnement.query.all():
        print(f"\n  Abonnement: {ab.naam} (ID: {ab.abonnement_id})")
        print(f"  Prijs: €{ab.prijs}/maand")
        print(f"  Betalingen:")
        for betaling in ab.betalingen:
            print(f"    - €{betaling.bedrag} ({betaling.status})")