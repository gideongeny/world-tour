import requests
import os

class LiteAPIService:
    def __init__(self):
        # Using sandbox keys provided by the user
        self.api_key = os.environ.get('LITEAPI_SANDBOX_KEY', 'sand_6e482b71-1bc4-4c45-b18c-cd0cd4977587')
        self.public_key = os.environ.get('LITEAPI_PUBLIC_KEY', 'cfff8058-e454-4bff-abaf-8e6f0b44d6bb')
        self.base_url = "https://api.liteapi.travel/v1"
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def search_hotels(self, destination_name, guests=2, checkin=None, checkout=None):
        """
        Search for hotels using LiteAPI.
        Note: LiteAPI usually requires a cityId or geocodes.
        We'll first resolve the destination to a cityId if possible or use a proxy search.
        """
        # Step 1: Search for the city to get coordinates/ID
        try:
            # First, try to find the city
            city_url = f"{self.base_url}/hotels/cities"
            city_params = {"name": destination_name}
            city_response = requests.get(city_url, headers=self.headers, params=city_params)
            
            city_data = city_response.json()
            if not city_data.get('data'):
                return []

            city_id = city_data['data'][0]['id']
            
            # Step 2: Search hotels in that city
            search_url = f"{self.base_url}/hotels/list-by-city"
            search_params = {
                "cityId": city_id,
                "adults": guests
            }
            if checkin: search_params["checkIn"] = checkin
            if checkout: search_params["checkOut"] = checkout
            
            response = requests.get(search_url, headers=self.headers, params=search_params)
            data = response.json()
            
            if data.get('data'):
                # Format to our Hotel interface
                return [{
                    'id': h.get('id'),
                    'name': h.get('name'),
                    'location': h.get('address', {}).get('city', destination_name),
                    'price': h.get('price', 100), # LiteAPI returns price in data usually
                    'rating': h.get('rating', 4.5),
                    'image_url': h.get('images', [{}])[0].get('url', 'https://images.unsplash.com/photo-1566073771259-6a8506099945'),
                    'description': h.get('description', 'Luxury accommodation through LiteAPI')
                } for h in data['data']]
                
            return []
        except Exception as e:
            print(f"LiteAPI Error: {str(e)}")
            return []

liteapi_service = LiteAPIService()
