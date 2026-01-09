from app import app, db
from new_models import Destination
import random

def expand_world_class_destinations():
    with app.app_context():
        # Curated list of elite destinations
        destinations = [
            {
                'name': 'Maasai Mara',
                'country': 'Kenya',
                'description': 'Experience the greatest wildlife show on earth - the Great Migration across the vast savannah.',
                'price': 450.0,
                'duration': 5,
                'image_url': 'https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&q=80',
                'category': 'safari',
                'latitude': -1.4061,
                'longitude': 35.0839,
                'climate': 'Tropical Savannah',
                'best_time_to_visit': 'July to October'
            },
            {
                'name': 'Diani Beach',
                'country': 'Kenya',
                'description': 'Pristine white sands and turquoise waters of the Indian Ocean, perfect for luxury relaxation.',
                'price': 280.0,
                'duration': 7,
                'image_url': 'https://images.unsplash.com/photo-1589192329731-00d98e16bb6e?auto=format&fit=crop&q=80',
                'category': 'beach',
                'latitude': -4.2797,
                'longitude': 39.5947,
                'climate': 'Tropical',
                'best_time_to_visit': 'December to March'
            },
            {
                'name': 'Santorini',
                'country': 'Greece',
                'description': 'Iconic blue-domed churches and breathtaking sunsets overlooking the Aegean Sea.',
                'price': 600.0,
                'duration': 4,
                'image_url': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&q=80',
                'category': 'luxury',
                'latitude': 36.3932,
                'longitude': 25.4615,
                'climate': 'Mediterranean',
                'best_time_to_visit': 'April to October'
            },
            {
                'name': 'Kyoto',
                'country': 'Japan',
                'description': 'The heart of traditional Japan, filled with ancient temples, zen gardens, and geisha districts.',
                'price': 350.0,
                'duration': 6,
                'image_url': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&q=80',
                'category': 'cultural',
                'latitude': 35.0116,
                'longitude': 135.7681,
                'climate': 'Temperate',
                'best_time_to_visit': 'March to May, October to November'
            },
            {
                'name': 'Amalfi Coast',
                'country': 'Italy',
                'description': 'A spectacular stretch of coastline featuring cliffside villages and crystal clear waters.',
                'price': 550.0,
                'duration': 5,
                'image_url': 'https://images.unsplash.com/photo-1533105079780-92b9be482077?auto=format&fit=crop&q=80',
                'category': 'luxury',
                'latitude': 40.6333,
                'longitude': 14.6029,
                'climate': 'Mediterranean',
                'best_time_to_visit': 'May to September'
            },
            {
                'name': 'Maldives',
                'country': 'Maldives',
                'description': 'The ultimate private island escape with overwater bungalows and vibrant coral reefs.',
                'price': 800.0,
                'duration': 6,
                'image_url': 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?auto=format&fit=crop&q=80',
                'category': 'beach',
                'latitude': 3.2028,
                'longitude': 73.2207,
                'climate': 'Tropical',
                'best_time_to_visit': 'November to April'
            },
            {
                'name': 'Swiss Alps',
                'country': 'Switzerland',
                'description': 'Majestic snow-capped peaks and pristine lakes, offering world-class skiing and hiking.',
                'price': 420.0,
                'duration': 6,
                'image_url': 'https://images.unsplash.com/photo-1531310197839-ccf54634509e?auto=format&fit=crop&q=80',
                'category': 'adventure',
                'latitude': 46.8182,
                'longitude': 8.2275,
                'climate': 'Alpine',
                'best_time_to_visit': 'December to March, June to August'
            },
            {
                'name': 'Bora Bora',
                'country': 'French Polynesia',
                'description': 'Often called the most beautiful island in the world, famous for its turquoise lagoon.',
                'price': 950.0,
                'duration': 5,
                'image_url': 'https://images.unsplash.com/photo-1532408840957-031d8030ae75?auto=format&fit=crop&q=80',
                'category': 'luxury',
                'latitude': -16.5004,
                'longitude': -151.7415,
                'climate': 'Tropical',
                'best_time_to_visit': 'May to October'
            },
            {
                'name': 'Cape Town',
                'country': 'South Africa',
                'description': 'A vibrant city where the mountains meet the sea, featuring Table Mountain and nearby wineries.',
                'price': 320.0,
                'duration': 6,
                'image_url': 'https://images.unsplash.com/photo-1580619305218-8423a7ef79b4?auto=format&fit=crop&q=80',
                'category': 'cultural',
                'latitude': -33.9249,
                'longitude': 18.4241,
                'climate': 'Mediterranean',
                'best_time_to_visit': 'November to March'
            },
            {
                'name': 'Serengeti',
                'country': 'Tanzania',
                'description': 'Endless plains teeming with predators and home to the massive migratory herds.',
                'price': 480.0,
                'duration': 5,
                'image_url': 'https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&q=80',
                'category': 'safari',
                'latitude': -2.3333,
                'longitude': 34.8333,
                'climate': 'Tropical Savannah',
                'best_time_to_visit': 'June to October'
            }
        ]

        # Add new destinations if they don't exist
        for d_data in destinations:
            existing = Destination.query.filter_by(name=d_data['name']).first()
            if not existing:
                dest = Destination(**d_data)
                db.session.add(dest)
                print(f"Added destination: {d_data['name']}")
            else:
                # Update existing one to have better image/coords
                existing.image_url = d_data['image_url']
                existing.latitude = d_data['latitude']
                existing.longitude = d_data['longitude']
                existing.price = d_data['price']
                print(f"Updated destination: {d_data['name']}")

        db.session.commit()
        print("Expansion complete!")

if __name__ == '__main__':
    expand_world_class_destinations()
