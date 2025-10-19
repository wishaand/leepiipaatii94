"""Database functionalty"""

import requests
from flask import current_app


def execute_query(query, values=None):
    """Calls the HBO-ICT.cloud API to execute a query."""
    url = current_app.config.get("API_URL")
    api_key = current_app.config.get("API_KEY")
    database = current_app.config.get("DATABASE")
    
    if not url or not api_key or not database:
        print("Warning: Database configuration missing. API_URL, API_KEY, or DATABASE not set.")
        return []
    
    url += "/db"

    x = requests.post(
        url=url,
        json={"query": query, "values": values, "database": database},
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=10,
    )
    return x.json()
