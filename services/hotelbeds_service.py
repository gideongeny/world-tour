import requests
import time
import hashlib
import os

class HotelbedsService:
    def __init__(self):
        self.api_key = os.environ.get('HOTELBEDS_API_KEY', '0f01a4e17c5508c923224a2ddf30c7d7')
        self.secret = os.environ.get('HOTELBEDS_API_SECRET', '') # Secret is usually needed for signature
        self.base_url = "https://api.test.hotelbeds.com/hotel-content-api/3.0" # Test environment

    def generate_signature(self):
        """Generates X-Signature for Hotelbeds API"""
        if not self.secret:
            return None
        
        timestamp = int(time.time())
        signature_raw = f"{self.api_key}{self.secret}{timestamp}"
        return hashlib.sha256(signature_raw.encode('utf-8')).hexdigest()

    def get_headers(self):
        signature = self.generate_signature()
        headers = {
            "Api-key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        if signature:
            headers["X-Signature"] = signature
        return headers

    def search_hotels(self, destination_code, checkin, checkout, guests=2):
        """
        Search for hotels using Hotelbeds API.
        Note: Hotelbeds uses destination codes (e.g. 'PAR' for Paris).
        """
        if not self.secret:
            print("Hotelbeds: No API Secret provided. Cannot generate signature.")
            return []

        url = "https://api.test.hotelbeds.com/hotel-booking-api/1.0/hotels"
        payload = {
            "stay": {
                "checkIn": checkin,
                "checkOut": checkout
            },
            "occupancies": [
                {
                    "rooms": 1,
                    "adults": guests,
                    "children": 0
                }
            ],
            "destination": {
                "code": destination_code
            }
        }

        try:
            response = requests.post(url, headers=self.get_headers(), json=payload)
            data = response.json()
            
            if data.get('hotels') and data['hotels'].get('hotels'):
                return [{
                    'id': h.get('code'),
                    'name': h.get('name'),
                    'location': h.get('destinationName', destination_code),
                    'price': h.get('minRate', 120),
                    'rating': float(h.get('categoryCode', '4').replace('ST', '')),
                    'image_url': 'https://images.unsplash.com/photo-1566073771259-6a8506099945',
                    'description': 'Luxury stay via Hotelbeds'
                } for h in data['hotels']['hotels']]
            
            return []
        except Exception as e:
            print(f"Hotelbeds Error: {str(e)}")
            return []

hotelbeds_service = HotelbedsService()
