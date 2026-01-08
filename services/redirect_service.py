import urllib.parse
from datetime import datetime

class RedirectService:
    @staticmethod
    def get_booking_url(destination, checkin=None, checkout=None, guests=2, rooms=1):
        """Generates a search URL for Booking.com"""
        base_url = "https://www.booking.com/searchresults.html"
        params = {
            "ss": destination,
            "group_adults": guests,
            "no_rooms": rooms,
            "aid": "304142" # Generic affiliate ID placeholder
        }
        
        if checkin and checkout:
            params["checkin"] = checkin
            params["checkout"] = checkout
            
        return f"{base_url}?{urllib.parse.urlencode(params)}"

    @staticmethod
    def get_skyscanner_url(origin, destination, date):
        """Generates a search URL for Skyscanner"""
        # Skyscanner usually uses a clean path: /transport/flights/lhr/jfk/240108/
        # If origin/dest are common names, we'll try a search query as fallback
        if len(origin) == 3 and len(destination) == 3:
            # IATA codes format
            date_str = date.replace("-", "")[2:] # YYYY-MM-DD to YYMMDD
            return f"https://www.skyscanner.net/transport/flights/{origin.lower()}/{destination.lower()}/{date_str}/"
        
        # Search query fallback
        query = f"flights from {origin} to {destination} on {date}"
        return f"https://www.google.com/search?q={urllib.parse.quote(query)}"

    @staticmethod
    def get_google_flights_url(origin, destination, date):
        """Generates a search URL for Google Flights"""
        return f"https://www.google.com/travel/flights?q=Flights%20to%20{urllib.parse.quote(destination)}%20from%20{urllib.parse.quote(origin)}%20on%20{date}"

redirect_service = RedirectService()
