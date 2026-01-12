from app import app, db
from new_models import Destination, Hotel
import random

def final_polish_data():
    with app.app_context():
        # 1. Update all destinations with correct coordinates and premium images
        premium_destinations = {
            'Maasai Mara': {
                'lat': -1.4061, 'lng': 35.0839, 
                'img': '/assets/hero/maasai-mara-hero.jpg',
                'desc': 'Experience the heart of the wild with the Great Migration.'
            },
            'Zanzibar': {
                'lat': -6.1659, 'lng': 39.2026, 
                'img': '/assets/hero/zanzibar-hero.jpg',
                'desc': 'Exotic spice island with pristine white sands and historic Stone Town.'
            },
            'Santorini': {
                'lat': 36.3932, 'lng': 25.4615, 
                'img': 'https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff',
                'desc': 'Timeless beauty with blue-domed architecture and caldera views.'
            },
            'Kyoto': {
                'lat': 35.0116, 'lng': 135.7681, 
                'img': 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e',
                'desc': 'Discover the soul of Japanese culture through ancient temples.'
            },
            'Amalfi Coast': {
                'lat': 40.6333, 'lng': 14.6029, 
                'img': 'https://images.unsplash.com/photo-1533105079780-92b9be482077',
                'desc': 'Italy\'s most iconic coastline with dramatic cliffs.'
            },
            'Shanghai': {
                'lat': 31.2304, 'lng': 121.4737, 
                'img': '/assets/hero/shanghai-hero.jpg',
                'desc': 'The Pearl of the Orient. Rated 4.7/5 for modern wonders.'
            },
            'Los Angeles': {
                'lat': 34.0522, 'lng': -118.2437, 
                'img': '/assets/hero/los-angeles-hero.jpg',
                'desc': 'City of Angels. Rated 4.6/5 for entertainment.'
            },
            'Dakar': {
                'lat': 14.7167, 'lng': -17.4677, 
                'img': '/assets/hero/dakar-hero.jpg',
                'desc': 'Gateway to Africa. Rated 4.5/5 for vibrance.'
            },
            'Dubai': {
                'lat': 25.2048, 'lng': 55.2708, 
                'img': 'https://images.unsplash.com/photo-1512453979798-5ea90b7cadc9',
                'desc': 'A futuristic oasis of luxury and architectural marvels.'
            },
            'Paris': {
                'lat': 48.8566, 'lng': 2.3522, 
                'img': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34',
                'desc': 'The City of Light, synonymous with romance and art.'
            }
        }

        for name, info in premium_destinations.items():
            dest = Destination.query.filter_by(name=name).first()
            if dest:
                dest.latitude = info['lat']
                dest.longitude = info['lng']
                dest.image_url = info['img'] + '?auto=format&fit=crop&q=80'
                dest.description = info['desc']
                print(f"Polished: {name}")

        # 2. Add some local Kenyan hotels for variety
        kenyan_hotels = [
            ('Sarova Mara Game Camp', 'Maasai Mara, Kenya', 450, 4.9, 'https://images.unsplash.com/photo-1493558103817-585a914050ef'),
            ('Baobab Beach Resort', 'Diani Beach, Kenya', 280, 4.7, 'https://images.unsplash.com/photo-1540541338287-41700207dee6'),
            ('Villa Rosa Kempinski', 'Nairobi, Kenya', 320, 5.0, 'https://images.unsplash.com/photo-1566073771259-6a8506099945')
        ]

        for name, loc, price, rating, img in kenyan_hotels:
            existing = Hotel.query.filter_by(name=name).first()
            if not existing:
                h = Hotel(
                    name=name,
                    location=loc,
                    price=price,
                    rating=rating,
                    image_url=img + '?auto=format&fit=crop&q=80',
                    description=f'Elite Kenyan hospitality at {name}'
                )
                db.session.add(h)
                print(f"Added Kenyan Hotel: {name}")

        db.session.commit()
        print("Final polish complete!")

if __name__ == '__main__':
    final_polish_data()
