from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from datetime import datetime, timedelta
import os
import json
import requests
import base64
from io import BytesIO
from flask_mail import Mail, Message
import uuid
import stripe
from flask_migrate import Migrate
from flask_babel import Babel, gettext, ngettext
import redis
from celery import Celery
from flask_cors import CORS

from functools import wraps
import pickle
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
import time
import logging
from flask_compress import Compress
from flask_caching import Cache
import random
from decorators import cache_result
import glob
from flask_login import LoginManager

# Handle missing Pillow gracefully
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Warning: Pillow not available. Image optimization features disabled.")

# Stripe configuration is managed in services/stripe_service.py

app = Flask(__name__)
CORS(app)

def get_locale():
    return 'en'

babel = Babel(app, locale_selector=get_locale)

# Database configuration for production
DATABASE_URL = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL') or 'sqlite:///world_tour_v3.db'
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'please-set-a-real-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

from new_models import User, Destination, Hotel, Flight, Booking, Review, WishlistItem, AITravelAssistant, UserAnalytics

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# Register Blueprints
from blueprints.booking.routes import booking_bp
from blueprints.ai.routes import ai_bp
from blueprints.auth.routes import auth_bp
from blueprints.affiliate.routes import affiliate_bp
from blueprints.payments.routes import payments_bp
from blueprints.user.routes import user_bp

app.register_blueprint(booking_bp, url_prefix='/booking')
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(affiliate_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(user_bp)

@app.route('/seed')
def seed_db():
    from new_models import Destination, Hotel, Flight
    
    try:
        # Clear existing data for fresh seed
        db.session.query(Flight).delete()
        db.session.query(Hotel).delete()
        # Only delete destinations if we plan to re-seed them, specifically if we want to update images
        # For this fix, let's update everything to be safe
        db.session.query(Destination).delete()
        db.session.commit()
        
        # 1. Destinations (Expanded with Curated High-Res Images & Realistic Data)
        destinations = [
            Destination(name='Paris', country='France', description='The City of Light. Rated 4.8/5 by travelers.', price=200, rating=4.8, duration=5, image_url='https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&q=80', category='cultural', latitude=48.8566, longitude=2.3522, climate='Temperate', best_time_to_visit='Spring', quote="Paris is always a good idea. — Audrey Hepburn"),
            Destination(name='Bali', country='Indonesia', description='Island of the Gods. Rated 4.9/5 by nature lovers.', price=150, rating=4.9, duration=7, image_url='https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&q=80', category='beach', latitude=-8.4095, longitude=115.1889, climate='Tropical', best_time_to_visit='Dry Season', quote="I think I deserve something beautiful. — Elizabeth Gilbert (Eat, Pray, Love)"),
            Destination(name='Maasai Mara', country='Kenya', description='Witness the Great Migration. Rated 5.0/5 for wildlife.', price=450, rating=5.0, duration=5, image_url='https://images.unsplash.com/photo-1516426122078-c23e76319801?auto=format&fit=crop&q=80', category='safari', latitude=-1.4061, longitude=35.0839, climate='Savannah', best_time_to_visit='July to October', quote="I never knew of a morning in Africa when I woke up that I was not happy. — Ernest Hemingway"),
            Destination(name='Diani Beach', country='Kenya', description='Pristine white sands. Rated 4.8/5 for relaxation.', price=280, rating=4.8, duration=7, image_url='https://images.unsplash.com/photo-1590523277543-a94d2e4eb00b?auto=format&fit=crop&q=80', category='beach', latitude=-4.2797, longitude=39.5947, climate='Tropical', best_time_to_visit='December to March', quote="The ocean stirs the heart, inspires the imagination and brings eternal joy to the soul. — Wyland"),
            Destination(name='Serengeti', country='Tanzania', description='Endless plains of wildlife. Rated 4.9/5 for safari.', price=480, rating=4.9, duration=6, image_url='https://images.unsplash.com/photo-1535941339077-2dd1c7963098?auto=format&fit=crop&q=80', category='safari', latitude=-2.3333, longitude=34.8333, climate='Savannah', best_time_to_visit='June to October', quote="The only man I envy is the man who has not yet been to Africa. — Richard Mullin"),
            Destination(name='Cape Town', country='South Africa', description='Ocean meets mountain. Rated 4.8/5 for scenery.', price=170, rating=4.8, duration=8, image_url='https://images.unsplash.com/photo-1580060839134-75a5edca2e99?auto=format&fit=crop&q=80', category='adventure', latitude=-33.9249, longitude=18.4241, climate='Mediterranean', best_time_to_visit='Summer', quote="The fairest cape we saw in the whole circumference of the earth. — Sir Francis Drake"),
            Destination(name='Dubai', country='UAE', description='Ultramodern luxury. Rated 4.5/5 for shopping.', price=350, rating=4.5, duration=4, image_url='https://images.unsplash.com/photo-1546412414-e1885259563a?auto=format&fit=crop&q=80', category='luxury', latitude=25.2048, longitude=55.2708, climate='Desert', best_time_to_visit='Winter', quote="The desert tells a different story every time one ventures on it. — Wilfred Thesiger"),
            Destination(name='Santorini', country='Greece', description='Iconic sunsets. Rated 4.9/5 for romance.', price=250, rating=4.9, duration=5, image_url='https://images.unsplash.com/photo-1570077188670-e3a8d69ac5ff?auto=format&fit=crop&q=80', category='luxury', latitude=36.3932, longitude=25.4615, climate='Mediterranean', best_time_to_visit='Summer', quote="Happy is the man, I thought, who, before dying, has the good fortune to sail the Aegean sea. — Nikos Kazantzakis"),
            Destination(name='Tokyo', country='Japan', description='Tradition meets future. Rated 4.7/5 for culture.', price=300, rating=4.7, duration=6, image_url='https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&q=80', category='city', latitude=35.6762, longitude=139.6503, climate='Temperate', best_time_to_visit='Autumn', quote="Tokyo would probably be the art director of the world. — Terry Gilliam"),
            Destination(name='New York', country='USA', description='The city that never sleeps. Rated 4.6/5 for energy.', price=280, rating=4.6, duration=4, image_url='https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&q=80', category='city', latitude=40.7128, longitude=-74.0060, climate='Temperate', best_time_to_visit='Fall', quote="The city seen from the Queensboro Bridge is always the city seen for the first time. — F. Scott Fitzgerald"),
            Destination(name='Maldives', country='Maldives', description='Tropical paradise. Rated 5.0/5 for honeymooners.', price=400, rating=5.0, duration=6, image_url='https://images.unsplash.com/photo-1514282401047-d79a71a590e8?auto=format&fit=crop&q=80', category='beach', latitude=3.2028, longitude=73.2207, climate='Tropical', best_time_to_visit='Winter', quote="Smell the sea and feel the sky. Let your soul and spirit fly. — Van Morrison"),
            Destination(name='Cairo', country='Egypt', description='Home of the Pyramids. Rated 4.7/5 for history.', price=180, rating=4.7, duration=5, image_url='https://images.unsplash.com/photo-1503177119275-0aa32b3a9368?auto=format&fit=crop&q=80', category='cultural', latitude=30.0444, longitude=31.2357, climate='Desert', best_time_to_visit='October to April', quote="Man fears Time, yet Time fears the Pyramids. — Arab Proverb"),
        ]
        
        destinations_map = {}
        for d in destinations:
            db.session.add(d)
            destinations_map[d.name] = d
        
        db.session.commit()
        
        # 2. Hotels
        hotels_data = [
            ('The Ritz Paris', 'Paris, France', 1200, 5.0, 'Paris'),
            ('Hotel Le Meurice', 'Paris, France', 900, 4.9, 'Paris'),
            ('Ayana Resort', 'Bali, Indonesia', 450, 4.8, 'Bali'),
            ('Viceroy Bali', 'Bali, Indonesia', 600, 4.9, 'Bali'),
            ('Aman Tokyo', 'Tokyo, Japan', 1100, 5.0, 'Tokyo'),
            ('Burj Al Arab', 'Dubai, UAE', 2500, 5.0, 'Dubai'),
        ]
        
        for name, location, price, rating, dest_name in hotels_data:
            dest = destinations_map.get(dest_name)
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
        
        # 3. Flights
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
        
        return jsonify({
            "message": "Database seeded successfully!",
            "destinations": Destination.query.count(),
            "hotels": Hotel.query.count(),
            "flights": Flight.query.count()
        })
    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        print(f"Seed Error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/populate')
def populate_data():
    from new_models import Destination, Hotel, Flight
    try:
        # Clear existing
        Hotel.query.delete()
        Flight.query.delete()
        db.session.commit()
        
        # Get destinations
        destinations_map = {}
        for name in ['Paris', 'Bali', 'Tokyo', 'Dubai', 'Santorini', 'Rome']:
            dest = Destination.query.filter_by(name=name).first()
            if dest:
                destinations_map[name] = dest
        
        # Custom high-quality images for hotels
        HOTEL_IMAGES = {
            'The Ritz Paris': 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800&q=80',
            'Hotel Le Meurice': 'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=800&q=80',
            'Ayana Resort': 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800&q=80', 
            'Viceroy Bali': 'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80',
            'Aman Tokyo': 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=800&q=80',
            'Park Hyatt Tokyo': 'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800&q=80',
            'Burj Al Arab': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800&q=80',
            'Atlantis The Palm': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80',
            'Canaves Oia': 'https://images.unsplash.com/photo-1613490493576-7fde63acd811?w=800&q=80',
            'Hotel Hassler Roma': 'https://images.unsplash.com/photo-1587974928442-77dc3e0dba72?w=800&q=80',
        }
        
        # Add Hotels
        hotels_data = [
            ('The Ritz Paris', 'Paris, France', 1200, 5.0, 'Paris'),
            ('Hotel Le Meurice', 'Paris, France', 900, 4.9, 'Paris'),
            ('Ayana Resort', 'Bali, Indonesia', 450, 4.8, 'Bali'),
            ('Viceroy Bali', 'Bali, Indonesia', 600, 4.9, 'Bali'),
            ('Aman Tokyo', 'Tokyo, Japan', 1100, 5.0, 'Tokyo'),
            ('Park Hyatt Tokyo', 'Tokyo, Japan', 800, 4.8, 'Tokyo'),
            ('Burj Al Arab', 'Dubai, UAE', 2500, 5.0, 'Dubai'),
            ('Atlantis The Palm', 'Dubai, UAE', 1800, 4.7, 'Dubai'),
            ('Canaves Oia', 'Santorini, Greece', 950, 4.9, 'Santorini'),
            ('Hotel Hassler Roma', 'Rome, Italy', 850, 4.8, 'Rome'),
        ]
        
        for name, location, price, rating, dest_name in hotels_data:
            dest = destinations_map.get(dest_name)
            if dest:
                # Use specific image if available, else a nice generic luxury room
                img_url = HOTEL_IMAGES.get(name, 'https://images.unsplash.com/photo-1566073771259-6a8506099945')
                
                hotel = Hotel(
                    name=name,
                    location=location,
                    price=price,
                    rating=rating,
                    destination_id=dest.id,
                    image_url=img_url,
                    description=f'Experience world-class service and luxury at {name}. Located in the heart of {location}, offering breathtaking views and exquisite dining.'
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
        
        return jsonify({
            'success': True,
            'hotels': Hotel.query.count(),
            'flights': Flight.query.count()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/currency/rates')
def get_currency_rates():
    from services.currency import currency_service
    try:
        rates = currency_service.get_rates()
        return jsonify({
            'success': True,
            'base': 'USD',
            'rates': rates,
            'last_update': currency_service.last_update.isoformat() if currency_service.last_update else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Performance optimizations
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache for static files
app.config['TEMPLATES_AUTO_RELOAD'] = True  # Enable auto-reload for development
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 20,
    'max_overflow': 0
}


# Enable compression
Compress(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
