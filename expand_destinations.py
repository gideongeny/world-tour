from app import app, db, Destination

def expand_destinations():
    with app.app_context():
        # List of high-quality, world-class destinations
        extra_destinations = [
            Destination(
                name='Maasai Mara',
                country='Kenya',
                description='The ultimate safari experience. Witness the Great Migration and the majestic Big Five in their natural habitat.',
                price=450.0,
                duration=5,
                image_url='https://images.unsplash.com/photo-1516422317184-268a25c7ce75?auto=format&fit=crop&q=80',
                category='adventure',
                latitude=-1.5271,
                longitude=35.1968,
                climate='Tropical Savannah',
                best_time_to_visit='July to October (Migration)'
            ),
            Destination(
                name='Kyoto',
                country='Japan',
                description='Step back in time in the city of ten thousand shrines, Zen gardens, and traditional tea ceremonies.',
                price=320.0,
                duration=7,
                image_url='https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&q=80',
                category='cultural',
                latitude=35.0116,
                longitude=135.7681,
                climate='Temperate',
                best_time_to_visit='April (Sakura) or November (Autumn colors)'
            ),
            Destination(
                name='Zanzibar',
                country='Tanzania',
                description='Explore the historic Stone Town and relax on the pristine white-sand beaches of the Spice Island.',
                price=280.0,
                duration=6,
                image_url='https://images.unsplash.com/photo-1586861635167-e5223aadc9fe?auto=format&fit=crop&q=80',
                category='beach',
                latitude=-6.1378,
                longitude=39.3621,
                climate='Tropical',
                best_time_to_visit='June to October'
            ),
            Destination(
                name='Venice',
                country='Italy',
                description='The world\'s most romantic city, floating on a lagoon with winding canals and historic palaces.',
                price=240.0,
                duration=4,
                image_url='https://images.unsplash.com/photo-1514890547357-a9ee288728e0?auto=format&fit=crop&q=80',
                category='cultural',
                latitude=45.4408,
                longitude=12.3155,
                climate='Humid Subtropical',
                best_time_to_visit='April to June, September to October'
            ),
            Destination(
                name='Great Barrier Reef',
                country='Australia',
                description='The world\'s largest coral reef system, offering unparalleled snorkeling and diving adventures.',
                price=380.0,
                duration=6,
                image_url='https://images.unsplash.com/photo-1544551763-47a0159f9234?auto=format&fit=crop&q=80',
                category='adventure',
                latitude=-18.2871,
                longitude=147.6992,
                climate='Tropical',
                best_time_to_visit='June to October'
            ),
            Destination(
                name='Diani Beach',
                country='Kenya',
                description='Award-winning beach with flawless white sands, turquoise waters, and world-class kite surfing.',
                price=220.0,
                duration=7,
                image_url='https://images.unsplash.com/photo-1584132967334-10e028bd69f7?auto=format&fit=crop&q=80',
                category='beach',
                latitude=-4.2792,
                longitude=39.5947,
                climate='Tropical',
                best_time_to_visit='December to March'
            ),
             Destination(
                name='Machu Picchu',
                country='Peru',
                description='The lost city of the Incas, perched high in the Andes mountains within a tropical forest.',
                price=350.0,
                duration=8,
                image_url='https://images.unsplash.com/photo-1526392060635-9d6019884377?auto=format&fit=crop&q=80',
                category='adventure',
                latitude=-13.1631,
                longitude=-72.5450,
                climate='Subtropical Highland',
                best_time_to_visit='May to September'
            )
        ]

        # Add destinations
        added_count = 0
        for destination in extra_destinations:
            # Check if destination already exists
            existing = Destination.query.filter_by(name=destination.name, country=destination.country).first()
            if not existing:
                db.session.add(destination)
                added_count += 1
                print(f"Added: {destination.name}, {destination.country}")
            else:
                # Update existing one if needed (optional)
                existing.image_url = destination.image_url
                print(f"Updated image for: {destination.name}")
        
        db.session.commit()
        print(f"\nExpanded destination list with {added_count} new world-class entries!")

if __name__ == '__main__':
    expand_destinations()
