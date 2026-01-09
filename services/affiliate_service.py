"""
Affiliate Service - Centralized affiliate link generation and tracking
Supports: Booking.com, Skyscanner, GetYourGuide, World Nomads
"""

class AffiliateService:
    # Affiliate IDs (Replace with your actual IDs after signing up)
    BOOKING_COM_AID = "YOUR_BOOKING_COM_AFFILIATE_ID"
    SKYSCANNER_AID = "YOUR_SKYSCANNER_AFFILIATE_ID"
    GETYOURGUIDE_AID = "YOUR_GETYOURGUIDE_PARTNER_ID"
    WORLD_NOMADS_AID = "YOUR_WORLD_NOMADS_AFFILIATE_ID"
    
    @staticmethod
    def get_hotel_link(destination, checkin=None, checkout=None, guests=2):
        """
        Generate Booking.com affiliate link
        Commission: 25-40% of booking value
        """
        base_url = "https://www.booking.com/searchresults.html"
        
        params = {
            'ss': destination,
            'aid': AffiliateService.BOOKING_COM_AID,
            'no_rooms': 1,
            'group_adults': guests
        }
        
        if checkin and checkout:
            params['checkin'] = checkin
            params['checkout'] = checkout
        
        from urllib.parse import urlencode
        return f"{base_url}?{urlencode(params)}"
    
    @staticmethod
    def get_flight_link(origin, destination, date, return_date=None):
        """
        Generate Skyscanner affiliate link
        Commission: Revenue per click + booking bonuses
        """
        base_url = "https://www.skyscanner.com/transport/flights"
        
        # Format: /origin/destination/date/return_date
        path = f"/{origin}/{destination}/{date}"
        if return_date:
            path += f"/{return_date}"
        
        # Add affiliate tracking
        params = f"?associateid={AffiliateService.SKYSCANNER_AID}"
        
        return f"{base_url}{path}{params}"
    
    @staticmethod
    def get_activity_link(activity_id, destination):
        """
        Generate GetYourGuide affiliate link
        Commission: 8% of booking value
        """
        base_url = "https://www.getyourguide.com"
        
        # Add affiliate parameters
        params = f"?partner_id={AffiliateService.GETYOURGUIDE_AID}&utm_medium=online_publisher"
        
        return f"{base_url}/activity/{activity_id}{params}"
    
    @staticmethod
    def get_insurance_link(destination, trip_cost, travelers=1):
        """
        Generate World Nomads insurance affiliate link
        Commission: 10-15% of policy cost
        """
        base_url = "https://www.worldnomads.com/travel-insurance"
        
        from urllib.parse import urlencode
        params = {
            'affiliate': AffiliateService.WORLD_NOMADS_AID,
            'destination': destination,
            'travelers': travelers,
            'trip_cost': trip_cost
        }
        
        return f"{base_url}?{urlencode(params)}"
    
    @staticmethod
    def track_click(affiliate_type, destination, user_id=None):
        """
        Track affiliate link clicks for analytics
        Store in database for conversion tracking
        """
        from models import db, AffiliateClick
        from datetime import datetime
        
        click = AffiliateClick(
            affiliate_type=affiliate_type,
            destination=destination,
            user_id=user_id,
            clicked_at=datetime.utcnow()
        )
        
        db.session.add(click)
        db.session.commit()
        
        return click.id
