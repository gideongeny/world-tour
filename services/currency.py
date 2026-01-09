import requests
from datetime import datetime, timedelta
import json

class CurrencyService:
    def __init__(self):
        self.api_url = "https://api.exchangerate-api.com/v4/latest/USD"
        self.rates = {}
        self.last_update = None
        self.cache_duration = timedelta(hours=24)
    
    def get_rates(self):
        """Get exchange rates, using cache if available"""
        now = datetime.now()
        
        # Check if cache is still valid
        if self.rates and self.last_update and (now - self.last_update) < self.cache_duration:
            return self.rates
        
        # Fetch new rates
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            self.rates = data.get('rates', {})
            self.last_update = now
            
            return self.rates
        except Exception as e:
            print(f"Error fetching exchange rates: {e}")
            # Return cached rates if available, otherwise default rates
            if self.rates:
                return self.rates
            
            # Fallback rates if API fails
            return {
                'USD': 1.0,
                'EUR': 0.85,
                'GBP': 0.73,
                'JPY': 110.5,
                'AUD': 1.35,
                'CAD': 1.25,
                'CHF': 0.92,
                'CNY': 6.45,
                'INR': 74.5,
                'KES': 130.0,
                'ZAR': 18.5
            }
    
    def convert(self, amount, from_currency='USD', to_currency='USD'):
        """Convert amount from one currency to another"""
        rates = self.get_rates()
        
        if from_currency == to_currency:
            return amount
        
        # Convert to USD first if needed
        if from_currency != 'USD':
            amount = amount / rates.get(from_currency, 1.0)
        
        # Convert from USD to target currency
        return amount * rates.get(to_currency, 1.0)

# Global instance
currency_service = CurrencyService()
