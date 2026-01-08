from app import app, db, Destination

def add_new_destinations():
    with app.app_context():
        # Check if destinations already exist
        existing_count = Destination.query.count()
        print(f"Current destinations in database: {existing_count}")
        
        # List of new destinations to add
        new_destinations = [
            # Europe
            Destination(
                name='Rome',
                country='Italy',
                description='Explore the Eternal City with its ancient ruins, Vatican City, and world-famous cuisine.',
                price=180.0,
                duration=8,
                image_url='/static/paris.jpg',  # Using existing image as placeholder
                category='cultural',
                latitude=41.9028,
                longitude=12.4964,
                climate='Mediterranean',
                best_time_to_visit='March to May, September to November'
            ),
            Destination(
                name='Barcelona',
                country='Spain',
                description='Experience the vibrant culture, stunning architecture by Gaudi, and beautiful Mediterranean beaches.',
                price=160.0,
                duration=7,
                image_url='/static/paris.jpg',
                category='cultural',
                latitude=41.3851,
                longitude=2.1734,
                climate='Mediterranean',
                best_time_to_visit='May to June, September to October'
            ),
            Destination(
                name='Amsterdam',
                country='Netherlands',
                description='Discover charming canals, world-class museums, and the unique Dutch culture.',
                price=170.0,
                duration=6,
                image_url='/static/paris.jpg',
                category='cultural',
                latitude=52.3676,
                longitude=4.9041,
                climate='Temperate',
                best_time_to_visit='April to May, September to October'
            ),
            Destination(
                name='Prague',
                country='Czech Republic',
                description='Wander through fairy-tale Gothic architecture and medieval streets.',
                price=140.0,
                duration=5,
                image_url='/static/paris.jpg',
                category='cultural',
                latitude=50.0755,
                longitude=14.4378,
                climate='Temperate',
                best_time_to_visit='March to May, September to November'
            ),
            Destination(
                name='Vienna',
                country='Austria',
                description='Immerse yourself in classical music, imperial palaces, and coffee house culture.',
                price=175.0,
                duration=6,
                image_url='/static/paris.jpg',
                category='cultural',
                latitude=48.2082,
                longitude=16.3738,
                climate='Temperate',
                best_time_to_visit='April to May, September to October'
            ),
            Destination(
                name='Budapest',
                country='Hungary',
                description='Experience the beautiful city split by the Danube with thermal baths and stunning architecture.',
                price=130.0,
                duration=5,
                image_url='/static/paris.jpg',
                category='cultural',
                latitude=47.4979,
                longitude=19.0402,
                climate='Temperate',
                best_time_to_visit='March to May, September to November'
            ),
            Destination(
                name='Santorini',
                country='Greece',
                description='Admire stunning white-washed buildings, blue domes, and breathtaking sunsets.',
                price=200.0,
                duration=7,
                image_url='/static/greece.jpg',
                category='luxury',
                latitude=36.3932,
                longitude=25.4615,
                climate='Mediterranean',
                best_time_to_visit='June to September'
            ),
            Destination(
                name='Swiss Alps',
                country='Switzerland',
                description='Experience majestic mountains perfect for skiing, hiking, and outdoor adventures.',
                price=250.0,
                duration=8,
                image_url='/static/paris.jpg',
                category='adventure',
                latitude=46.8182,
                longitude=8.2275,
                climate='Alpine',
                best_time_to_visit='December to March (skiing), June to September (hiking)'
            ),
            
            # Asia
            Destination(
                name='Bangkok',
                country='Thailand',
                description='Explore vibrant street markets, ornate temples, and delicious street food.',
                price=120.0,
                duration=6,
                image_url='/static/tokyo.jpg',
                category='cultural',
                latitude=13.7563,
                longitude=100.5018,
                climate='Tropical',
                best_time_to_visit='November to March'
            ),
            Destination(
                name='Seoul',
                country='South Korea',
                description='Discover the perfect blend of ancient traditions and modern technology.',
                price=150.0,
                duration=7,
                image_url='/static/tokyo.jpg',
                category='cultural',
                latitude=37.5665,
                longitude=126.9780,
                climate='Temperate',
                best_time_to_visit='March to May, September to November'
            ),
            Destination(
                name='Singapore',
                country='Singapore',
                description='Experience the futuristic city-state with diverse cultures and amazing food.',
                price=180.0,
                duration=5,
                image_url='/static/tokyo.jpg',
                category='luxury',
                latitude=1.3521,
                longitude=103.8198,
                climate='Tropical',
                best_time_to_visit='February to April, July to September'
            ),
            Destination(
                name='Bali',
                country='Indonesia',
                description='Relax in tropical paradise with beautiful beaches, temples, and rice terraces.',
                price=140.0,
                duration=8,
                image_url='/static/maldives.jpg',
                category='beach',
                latitude=-8.3405,
                longitude=115.0920,
                climate='Tropical',
                best_time_to_visit='April to October'
            ),
            Destination(
                name='Hong Kong',
                country='China',
                description='Explore the vibrant metropolis with stunning skyline and diverse culture.',
                price=160.0,
                duration=6,
                image_url='/static/tokyo.jpg',
                category='cultural',
                latitude=22.3193,
                longitude=114.1694,
                climate='Subtropical',
                best_time_to_visit='October to December'
            ),
            Destination(
                name='Dubai',
                country='UAE',
                description='Experience luxury shopping, futuristic architecture, and desert adventures.',
                price=220.0,
                duration=7,
                image_url='/static/luxury.jpg',
                category='luxury',
                latitude=25.2048,
                longitude=55.2708,
                climate='Desert',
                best_time_to_visit='November to March'
            ),
            Destination(
                name='Mumbai',
                country='India',
                description='Discover the bustling financial capital with rich history and diverse culture.',
                price=110.0,
                duration=6,
                image_url='/static/tokyo.jpg',
                category='cultural',
                latitude=19.0760,
                longitude=72.8777,
                climate='Tropical',
                best_time_to_visit='November to March'
            ),
            
            # Americas
            Destination(
                name='Rio de Janeiro',
                country='Brazil',
                description='Experience the vibrant culture, beautiful beaches, and iconic Christ the Redeemer.',
                price=160.0,
                duration=7,
                image_url='/static/ny.jpg',
                category='beach',
                latitude=-22.9068,
                longitude=-43.1729,
                climate='Tropical',
                best_time_to_visit='March to May, September to November'
            ),
            Destination(
                name='Mexico City',
                country='Mexico',
                description='Explore ancient Aztec ruins, colonial architecture, and vibrant street life.',
                price=130.0,
                duration=6,
                image_url='/static/ny.jpg',
                category='cultural',
                latitude=19.4326,
                longitude=-99.1332,
                climate='Subtropical',
                best_time_to_visit='March to May, September to November'
            ),
            Destination(
                name='Buenos Aires',
                country='Argentina',
                description='Experience the Paris of South America with tango, great food, and European charm.',
                price=140.0,
                duration=7,
                image_url='/static/ny.jpg',
                category='cultural',
                latitude=-34.6118,
                longitude=-58.3960,
                climate='Temperate',
                best_time_to_visit='March to May, September to November'
            ),
            Destination(
                name='Lima',
                country='Peru',
                description='Discover the culinary capital of South America with rich history and amazing food.',
                price=120.0,
                duration=5,
                image_url='/static/ny.jpg',
                category='cultural',
                latitude=-12.0464,
                longitude=-77.0428,
                climate='Desert',
                best_time_to_visit='December to April'
            ),
            Destination(
                name='Santiago',
                country='Chile',
                description='Explore the modern capital surrounded by the Andes mountains and wine regions.',
                price=150.0,
                duration=6,
                image_url='/static/ny.jpg',
                category='cultural',
                latitude=-33.4489,
                longitude=-70.6693,
                climate='Mediterranean',
                best_time_to_visit='September to November, March to May'
            ),
            
            # Africa
            Destination(
                name='Marrakech',
                country='Morocco',
                description='Get lost in the magical medina, vibrant souks, and beautiful riads.',
                price=130.0,
                duration=6,
                image_url='/static/cape.jpg',
                category='cultural',
                latitude=31.6295,
                longitude=-7.9811,
                climate='Desert',
                best_time_to_visit='March to May, September to November'
            ),
            Destination(
                name='Cairo',
                country='Egypt',
                description='Explore ancient pyramids, the Sphinx, and the fascinating Egyptian Museum.',
                price=140.0,
                duration=7,
                image_url='/static/cape.jpg',
                category='cultural',
                latitude=30.0444,
                longitude=31.2357,
                climate='Desert',
                best_time_to_visit='October to April'
            ),
            Destination(
                name='Nairobi',
                country='Kenya',
                description='Experience wildlife safaris, national parks, and vibrant African culture.',
                price=180.0,
                duration=8,
                image_url='/static/cape.jpg',
                category='adventure',
                latitude=-1.2921,
                longitude=36.8219,
                climate='Tropical',
                best_time_to_visit='July to September, January to February'
            ),
            Destination(
                name='Cape Town',
                country='South Africa',
                description='Discover stunning landscapes, Table Mountain, and beautiful beaches.',
                price=160.0,
                duration=7,
                image_url='/static/cape.jpg',
                category='adventure',
                latitude=-33.9249,
                longitude=18.4241,
                climate='Mediterranean',
                best_time_to_visit='March to May, September to November'
            ),
            
            # Oceania
            Destination(
                name='Sydney',
                country='Australia',
                description='Experience the iconic Opera House, beautiful beaches, and vibrant city life.',
                price=200.0,
                duration=8,
                image_url='/static/ny.jpg',
                category='beach',
                latitude=-33.8688,
                longitude=151.2093,
                climate='Temperate',
                best_time_to_visit='September to November, March to May'
            ),
            Destination(
                name='Auckland',
                country='New Zealand',
                description='Explore the City of Sails with stunning harbors and outdoor adventures.',
                price=180.0,
                duration=7,
                image_url='/static/ny.jpg',
                category='adventure',
                latitude=-36.8485,
                longitude=174.7633,
                climate='Temperate',
                best_time_to_visit='December to February, March to May'
            ),
            Destination(
                name='Fiji',
                country='Fiji',
                description='Relax in tropical paradise with crystal-clear waters and pristine beaches.',
                price=220.0,
                duration=8,
                image_url='/static/maldives.jpg',
                category='beach',
                latitude=-17.7134,
                longitude=178.0650,
                climate='Tropical',
                best_time_to_visit='May to October'
            )
        ]
        
        # Add new destinations
        added_count = 0
        for destination in new_destinations:
            # Check if destination already exists
            existing = Destination.query.filter_by(name=destination.name, country=destination.country).first()
            if not existing:
                db.session.add(destination)
                added_count += 1
                print(f"Added: {destination.name}, {destination.country}")
            else:
                print(f"Already exists: {destination.name}, {destination.country}")
        
        # Commit changes
        db.session.commit()
        
        print(f"\nAdded {added_count} new destinations!")
        print(f"Total destinations in database: {Destination.query.count()}")

if __name__ == '__main__':
    add_new_destinations() 