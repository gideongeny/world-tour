from app import app, db
from new_models import Destination, Hotel, Flight
from datetime import datetime, timedelta

with app.app_context():
    # Clear existing hotels and flights
    Hotel.query.delete()
    Flight.query.delete()
    db.session.commit()
    
    # Get destinations
    paris = Destination.query.filter_by(name='Paris').first()
    bali = Destination.query.filter_by(name='Bali').first()
    tokyo = Destination.query.filter_by(name='Tokyo').first()
    dubai = Destination.query.filter_by(name='Dubai').first()
    santorini = Destination.query.filter_by(name='Santorini').first()
    rome = Destination.query.filter_by(name='Rome').first()
    
    # Add Hotels
    hotels_data = [
        ('The Ritz Paris', 'Paris, France', 1200, 5.0, paris),
        ('Hotel Le Meurice', 'Paris, France', 900, 4.9, paris),
        ('Ayana Resort', 'Bali, Indonesia', 450, 4.8, bali),
        ('Viceroy Bali', 'Bali, Indonesia', 600, 4.9, bali),
        ('Aman Tokyo', 'Tokyo, Japan', 1100, 5.0, tokyo),
        ('Park Hyatt Tokyo', 'Tokyo, Japan', 800, 4.8, tokyo),
        ('Burj Al Arab', 'Dubai, UAE', 2500, 5.0, dubai),
        ('Atlantis The Palm', 'Dubai, UAE', 1800, 4.7, dubai),
        ('Canaves Oia', 'Santorini, Greece', 950, 4.9, santorini),
        ('Hotel Hassler Roma', 'Rome, Italy', 850, 4.8, rome),
    ]
    
    for name, location, price, rating, dest in hotels_data:
        if dest:
            hotel = Hotel(
                name=name,
                location=location,
                price=price,
                rating=rating,
                destination_id=dest.id,
                image_url='https://images.unsplash.com/photo-1566073771259-6a8506099945',
                description=f'Luxury accommodation in {location}'
            )
            db.session.add(hotel)
    
    # Add Flights
    now = datetime.now()
    flights_data = [
        ('Emirates', 'JFK (New York)', 'DXB (Dubai)', 1200, 2, '12h 30m', 'EK201'),
        ('Air France', 'JFK (New York)', 'CDG (Paris)', 800, 5, '7h 20m', 'AF007'),
        ('JAL', 'LAX (Los Angeles)', 'HND (Tokyo)', 1100, 34, '11h 45m', 'JL061'),
        ('Singapore Airlines', 'LHR (London)', 'SIN (Singapore)', 950, 8, '13h 10m', 'SQ308'),
        ('Qatar Airways', 'LHR (London)', 'DOH (Doha)', 850, 3, '6h 45m', 'QR004'),
        ('British Airways', 'LHR (London)', 'JFK (New York)', 650, 4, '7h 55m', 'BA117'),
        ('Lufthansa', 'FRA (Frankfurt)', 'LHR (London)', 200, 1, '1h 30m', 'LH904'),
        ('Delta', 'ATL (Atlanta)', 'LHR (London)', 900, 6, '8h 15m', 'DL030'),
        ('Etihad', 'JFK (New York)', 'AUH (Abu Dhabi)', 1150, 3, '12h 15m', 'EY101'),
        ('Turkish Airlines', 'IST (Istanbul)', 'JFK (New York)', 750, 5, '10h 30m', 'TK001'),
    ]
    
    for airline, origin, dest, price, hours, duration, flight_num in flights_data:
        flight = Flight(
            airline=airline,
            origin=origin,
            destination=dest,
            price=price,
            departure_time=now + timedelta(hours=hours),
            duration=duration,
            flight_number=flight_num
        )
        db.session.add(flight)
    
    db.session.commit()
    
    print(f'Successfully added {Hotel.query.count()} hotels')
    print(f'Successfully added {Flight.query.count()} flights')
    print('Database populated!')
