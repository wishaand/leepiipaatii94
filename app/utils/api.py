import os
import requests
from flask import current_app

class HBOICTCloud:
    def __init__(self):
        self.api_url = current_app.config['API_URL']
        self.api_key = current_app.config['API_KEY']
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def make_request(self, endpoint, method='GET', data=None):
        url = f"{self.api_url}/{endpoint}"
        response = requests.request(
            method,
            url,
            headers=self.headers,
            json=data
        )
        return response.json()