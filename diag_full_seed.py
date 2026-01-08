import os
import sys
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.getcwd())

from app import app, db
from new_models import Destination, Hotel, Flight

print("--- Running Full Seed Diagnostic ---")

with app.app_context():
    try:
        print("Creating tables...")
        db.create_all()
        
        # 1. Clear Data
        print("Clearing data...")
        db.session.query(Flight).delete()
        db.session.query(Hotel).delete()
        db.session.query(Destination).delete()
        db.session.commit()
        print("Data cleared.")
        
        # 2. Add Destinations
        print("Adding destinations...")
        destinations = [
            Destination(name='Paris', country='France', description='The City of Light.', price=200, duration=5, image_url='https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&q=80', category='cultural', latitude=48.8566, longitude=2.3522, climate='Temperate', best_time_to_visit='Spring'),
            Destination(name='Bali', country='Indonesia', description='Island of the Gods.', price=150, duration=7, image_url='https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&q=80', category='beach', latitude=-8.4095, longitude=115.1889, climate='Tropical', best_time_to_visit='Dry Season'),
            Destination(name='Tokyo', country='Japan', description='Tradition meets future.', price=300, duration=6, image_url='https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&q=80', category='city', latitude=35.6762, longitude=139.6503, climate='Temperate', best_time_to_visit='Autumn'),
            Destination(name='Dubai', country='UAE', description='Ultramodern luxury.', price=350, duration=4, image_url='https://images.unsplash.com/photo-1512453979798-5ea90b7cadc9?auto=format&fit=crop&q=80', category='luxury', latitude=25.2048, longitude=55.2708, climate='Desert', best_time_to_visit='Winter')
        ]
        
        dest_map = {}
        for d in destinations:
            db.session.add(d)
        db.session.commit()
        for d in destinations:
            dest_map[d.name] = d
        print(f"Added {len(destinations)} destinations.")
        
        # 3. Add Hotels
        print("Adding hotels...")
        hotels_data = [
            ('The Ritz Paris', 'Paris, France', 1200, 5.0, 'Paris'),
            ('Burj Al Arab', 'Dubai, UAE', 2500, 5.0, 'Dubai')
        ]
        for name, location, price, rating, d_name in hotels_data:
            d = dest_map.get(d_name)
            if d:
                h = Hotel(
                    name=name, location=location, price=price, rating=rating,
                    destination_id=d.id,
                    image_url='http://hotel.jpg', description='Desc'
                )
                db.session.add(h)
        db.session.commit()
        print("Added hotels.")
        
        # 4. Add Flights
        print("Adding flights...")
        now = datetime.now()
        f = Flight(
            airline='Emirates', origin='JFK', destination='DXB',
            price=1200, departure_time=now + timedelta(hours=2),
            duration='12h 30m', flight_number='EK201'
        )
        db.session.add(f)
        db.session.commit()
        print("Added flights.")
        
        print("\n--- ALL SEEDING SUCCESSFUL ---")
        
    except Exception as e:
        print("\n!!! SEEDING FAILED !!!")
        import traceback
        traceback.print_exc()
        print(f"Error type: {type(e)}")
        print(f"Error message: {str(e)}")
