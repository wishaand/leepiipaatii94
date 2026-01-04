import os                          # Omgevingsvariabelen uitlezen
import requests                    # HTTP requests versturen
from flask import current_app      # Flask app configuratie

class HBOICTCloud:
    """Klasse voor communicatie met HBO ICT Cloud API"""
    
    def __init__(self):
        """Initialiseer API client met sleutels en headers"""
        self.api_url = current_app.config['API_URL']
        # API adres uit Flask configuratie (bijv. https://api.example.com)
        
        self.api_key = current_app.config['API_KEY']
        # Geheime API sleutel uit Flask configuratie
        
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            # Authorization header met Bearer token (beveiliging)
            
            'Content-Type': 'application/json'
            # Zeg dat we JSON data sturen
        }

    def make_request(self, endpoint, method='GET', data=None):
        """Verstuur request naar API"""
        url = f"{self.api_url}/{endpoint}"
        # Maak volledige URL (bijv. https://api.example.com/users)
        
        response = requests.request(
            method,
            # HTTP methode: GET, POST, PUT, DELETE
            
            url,
            # De URL waar we naar versturen
            
            headers=self.headers,
            # Authorization en Content-Type headers
            
            json=data
            # JSON data om te versturen (bij POST/PUT)
        )
        
        return response.json()
        # Zet response om naar Python dictionary en return