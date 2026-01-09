from app import app, db, Destination

def final_destination_expansion():
    with app.app_context():
        new_items = [
            Destination(
                name='Amalfi Coast',
                country='Italy',
                description='Dramatic cliffs, azure waters, and pastel-colored villages clinging to the mountainside.',
                price=300.0,
                duration=6,
                image_url='https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&q=80',
                category='luxury',
                latitude=40.6333,
                longitude=14.6029,
                climate='Mediterranean',
                best_time_to_visit='May to September'
            ),
            Destination(
                name='Petra',
                country='Jordan',
                description='The world-famous archaeological site in Jordan\'s southwestern desert, dating to around 300 BC.',
                price=190.0,
                duration=5,
                image_url='https://images.unsplash.com/photo-1579606031850-029633734055?auto=format&fit=crop&q=80',
                category='cultural',
                latitude=30.3285,
                longitude=35.4444,
                climate='Arid',
                best_time_to_visit='March to May, September to November'
            ),
            Destination(
                name='Mombasa',
                country='Kenya',
                description='Coastal city blending history, culture, and stunning Indian Ocean beaches.',
                price=150.0,
                duration=5,
                image_url='https://images.unsplash.com/photo-1580910051074-3eb694886505?auto=format&fit=crop&q=80',
                category='beach',
                latitude=-4.0435,
                longitude=39.6682,
                climate='Tropical',
                best_time_to_visit='December to March'
            ),
            Destination(
                name='Iceland',
                country='Iceland',
                description='Land of fire and ice, with dramatic landscapes including volcanoes, geysers, and the Northern Lights.',
                price=280.0,
                duration=7,
                image_url='https://images.unsplash.com/photo-1476610182048-b716b8518aae?auto=format&fit=crop&q=80',
                category='adventure',
                latitude=64.9631,
                longitude=-19.0208,
                climate='Subarctic',
                best_time_to_visit='June to August (hiking), November to February (aurora)'
            )
        ]

        for item in new_items:
            existing = Destination.query.filter_by(name=item.name).first()
            if not existing:
                db.session.add(item)
                print(f"Added: {item.name}")
            else:
                existing.image_url = item.image_url
                print(f"Updated: {item.name}")
        
        db.session.commit()
        print("\nDestination update complete!")

if __name__ == '__main__':
    final_destination_expansion()
