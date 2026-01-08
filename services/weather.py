import os
import requests
from flask_caching import Cache

class WeatherService:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"

    def get_weather(self, city):
        if not self.api_key:
            # Fallback mock data
            return {
                'temp': 20,
                'condition': 'Sunny (Demo)',
                'humidity': 50,
                'description': 'Please set OPENWEATHER_API_KEY for real-time data.'
            }

        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            return {
                'temp': round(data['main']['temp']),
                'condition': data['weather'][0]['main'],
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon']
            }
        except Exception as e:
            print(f"Weather API error: {e}")
            return None

weather_service = WeatherService()
