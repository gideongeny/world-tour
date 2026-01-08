from app import app, db
from app import User, Destination, Booking, Review, Contact, WishlistItem, Newsletter, Flight, Hotel, RoomType, PackageDeal
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create admin user if not exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@worldtour.com',
                password_hash=generate_password_hash('admin123'),
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            db.session.add(admin_user)
        
        # Add sample flights if they don't exist
        if Flight.query.count() == 0:
            flights = [
                Flight(
                    flight_number='AA123',
                    airline='American Airlines',
                    origin='New York',
                    destination='Paris',
                    departure_time=datetime.now() + timedelta(days=7),
                    arrival_time=datetime.now() + timedelta(days=7, hours=7),
                    price=450.0,
                    seats_available=50
                ),
                Flight(
                    flight_number='BA456',
                    airline='British Airways',
                    origin='London',
                    destination='Tokyo',
                    departure_time=datetime.now() + timedelta(days=10),
                    arrival_time=datetime.now() + timedelta(days=10, hours=11),
                    price=800.0,
                    seats_available=30
                ),
                Flight(
                    flight_number='LH789',
                    airline='Lufthansa',
                    origin='Berlin',
                    destination='New York',
                    departure_time=datetime.now() + timedelta(days=5),
                    arrival_time=datetime.now() + timedelta(days=5, hours=8),
                    price=600.0,
                    seats_available=45
                ),
                Flight(
                    flight_number='EK101',
                    airline='Emirates',
                    origin='Dubai',
                    destination='Maldives',
                    departure_time=datetime.now() + timedelta(days=3),
                    arrival_time=datetime.now() + timedelta(days=3, hours=4),
                    price=350.0,
                    seats_available=60
                )
            ]
            
            for flight in flights:
                db.session.add(flight)
        
        # Add sample hotels if they don't exist
        if Hotel.query.count() == 0:
            hotels = [
                Hotel(
                    name='Grand Hotel Paris',
                    location='Paris, France',
                    description='Luxury hotel in the heart of Paris with stunning views of the Eiffel Tower.',
                    image_url='/static/hotel_paris.jpg',
                    rating=4.8
                ),
                Hotel(
                    name='Tokyo Imperial Hotel',
                    location='Tokyo, Japan',
                    description='Historic luxury hotel offering traditional Japanese hospitality.',
                    image_url='/static/hotel_tokyo.jpg',
                    rating=4.9
                ),
                Hotel(
                    name='New York Plaza Hotel',
                    location='New York, USA',
                    description='Iconic luxury hotel in Manhattan with world-class amenities.',
                    image_url='/static/hotel_ny.jpg',
                    rating=4.7
                ),
                Hotel(
                    name='Maldives Paradise Resort',
                    location='Maldives',
                    description='Overwater bungalows with private pools and ocean views.',
                    image_url='/static/hotel_maldives.jpg',
                    rating=4.9
                )
            ]
            
            for hotel in hotels:
                db.session.add(hotel)
            
            db.session.commit()
            
            # Add room types for each hotel
            hotels = Hotel.query.all()
            for hotel in hotels:
                room_types = [
                    RoomType(
                        hotel_id=hotel.id,
                        name='Standard Room',
                        description='Comfortable room with basic amenities',
                        price_per_night=150.0,
                        total_rooms=20,
                        available_rooms=15
                    ),
                    RoomType(
                        hotel_id=hotel.id,
                        name='Deluxe Room',
                        description='Spacious room with premium amenities',
                        price_per_night=250.0,
                        total_rooms=15,
                        available_rooms=10
                    ),
                    RoomType(
                        hotel_id=hotel.id,
                        name='Suite',
                        description='Luxury suite with separate living area',
                        price_per_night=400.0,
                        total_rooms=5,
                        available_rooms=3
                    )
                ]
                
                for room_type in room_types:
                    db.session.add(room_type)
        
        # Add sample destinations if they don't exist
        if Destination.query.count() == 0:
            destinations = [
                Destination(
                    name='Paris',
                    country='France',
                    description='Experience the magic of the City of Light with its iconic Eiffel Tower, world-class museums, and charming cafes.',
                    price=150.0,
                    duration=7,
                    image_url='/static/paris.jpg',
                    category='luxury',
                    latitude=48.8566,
                    longitude=2.3522,
                    climate='Temperate',
                    best_time_to_visit='April to October'
                ),
                Destination(
                    name='Tokyo',
                    country='Japan',
                    description='Discover the perfect blend of tradition and innovation in this vibrant metropolis.',
                    price=200.0,
                    duration=10,
                    image_url='/static/tokyo.jpg',
                    category='adventure',
                    latitude=35.6762,
                    longitude=139.6503,
                    climate='Temperate',
                    best_time_to_visit='March to May and September to November'
                ),
                Destination(
                    name='New York',
                    country='USA',
                    description='The city that never sleeps offers endless entertainment, shopping, and cultural experiences.',
                    price=180.0,
                    duration=8,
                    image_url='/static/ny.jpg',
                    category='luxury',
                    latitude=40.7128,
                    longitude=-74.0060,
                    climate='Humid subtropical',
                    best_time_to_visit='April to June and September to November'
                ),
                Destination(
                    name='Greece',
                    country='Greece',
                    description='Explore ancient ruins, beautiful islands, and Mediterranean cuisine in this historic paradise.',
                    price=120.0,
                    duration=6,
                    image_url='/static/greece.jpg',
                    category='budget',
                    latitude=39.0742,
                    longitude=21.8243,
                    climate='Mediterranean',
                    best_time_to_visit='May to October'
                ),
                Destination(
                    name='Maldives',
                    country='Maldives',
                    description='Paradise on earth with crystal clear waters, white sandy beaches, and overwater bungalows.',
                    price=300.0,
                    duration=12,
                    image_url='/static/maldives.jpg',
                    category='luxury',
                    latitude=3.2028,
                    longitude=73.2207,
                    climate='Tropical',
                    best_time_to_visit='November to April'
                ),
                Destination(
                    name='Cape Town',
                    country='South Africa',
                    description='A stunning coastal city with Table Mountain, beautiful beaches, and rich cultural heritage.',
                    price=140.0,
                    duration=9,
                    image_url='/static/cape.jpg',
                    category='adventure',
                    latitude=-33.9249,
                    longitude=18.4241,
                    climate='Mediterranean',
                    best_time_to_visit='March to May and September to November'
                ),
                Destination(
                    name='Mount Fuji',
                    country='Japan',
                    description='Climb Japan\'s most iconic mountain and experience breathtaking views of the surrounding landscape.',
                    price=100.0,
                    duration=5,
                    image_url='/static/mountfuji.jpg',
                    category='adventure',
                    latitude=35.3606,
                    longitude=138.7274,
                    climate='Temperate',
                    best_time_to_visit='July to September'
                )
            ]
            
            for destination in destinations:
                db.session.add(destination)
        
        # Add sample package deals if they don't exist
        if PackageDeal.query.count() == 0:
            # Get existing flights and hotels
            flights = Flight.query.all()
            hotels = Hotel.query.all()
            
            if flights and hotels:
                package_deals = [
                    PackageDeal(
                        name='Paris Luxury Getaway',
                        description='7-day luxury package including round-trip flight and 5-star hotel accommodation with guided tours.',
                        price=1200.0,
                        flight_id=flights[0].id if flights else None,
                        hotel_id=hotels[0].id if hotels else None,
                        activities='Eiffel Tower Tour, Louvre Museum Visit, Seine River Cruise, Wine Tasting, Shopping at Champs-Élysées',
                        image_url='/static/paris.jpg'
                    ),
                    PackageDeal(
                        name='Tokyo Adventure Package',
                        description='10-day adventure package with cultural experiences and modern city exploration.',
                        price=1800.0,
                        flight_id=flights[1].id if len(flights) > 1 else None,
                        hotel_id=hotels[1].id if len(hotels) > 1 else None,
                        activities='Mount Fuji Tour, Traditional Tea Ceremony, Sushi Making Class, Akihabara Electronics Tour, Shibuya Crossing Experience',
                        image_url='/static/tokyo.jpg'
                    ),
                    PackageDeal(
                        name='Maldives Paradise Escape',
                        description='5-day tropical paradise with water activities and relaxation.',
                        price=2500.0,
                        flight_id=flights[3].id if len(flights) > 3 else None,
                        hotel_id=hotels[3].id if len(hotels) > 3 else None,
                        activities='Snorkeling, Sunset Cruise, Spa Treatment, Beach Yoga, Island Hopping, Water Sports',
                        image_url='/static/maldives.jpg'
                    ),
                    PackageDeal(
                        name='New York City Experience',
                        description='8-day urban adventure in the city that never sleeps.',
                        price=1500.0,
                        flight_id=flights[2].id if len(flights) > 2 else None,
                        hotel_id=hotels[2].id if len(hotels) > 2 else None,
                        activities='Broadway Show, Central Park Tour, Empire State Building, Times Square, Brooklyn Bridge Walk, Shopping at Fifth Avenue',
                        image_url='/static/ny.jpg'
                    )
                ]
                
                for package in package_deals:
                    db.session.add(package)

        db.session.commit()
        print("Database initialized successfully!")

if __name__ == '__main__':
    init_db() 