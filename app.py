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

# Stripe configuration (test keys)
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_placeholder')
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', 'pk_test_placeholder')

app = Flask(__name__)
CORS(app)

# Database configuration for production
DATABASE_URL = os.environ.get('POSTGRES_URL') or os.environ.get('DATABASE_URL') or 'sqlite:///world_tour.db'
if DATABASE_URL.startswith('postgres://'):
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

from new_models import User
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

# Register Blueprints
from blueprints.booking.routes import booking_bp
from blueprints.ai.routes import ai_bp
from blueprints.auth.routes import auth_bp

app.register_blueprint(booking_bp, url_prefix='/booking')
app.register_blueprint(ai_bp, url_prefix='/ai')
app.register_blueprint(auth_bp, url_prefix='/auth')

@app.route('/seed')
def seed_db():
    from new_models import Destination, Hotel, Flight
    
    try:
        # Clear existing data for fresh seed
        db.session.query(Flight).delete()
        db.session.query(Hotel).delete()
        db.session.commit()
        
        # 1. Destinations (Expanded)
        destinations = [
            Destination(name='Paris', country='France', description='The City of Light.', price=200, duration=5, image_url='https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&q=80', category='cultural', latitude=48.8566, longitude=2.3522, climate='Temperate', best_time_to_visit='Spring'),
            Destination(name='Bali', country='Indonesia', description='Island of the Gods.', price=150, duration=7, image_url='https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&q=80', category='beach', latitude=-8.4095, longitude=115.1889, climate='Tropical', best_time_to_visit='Dry Season'),
            Destination(name='Tokyo', country='Japan', description='Tradition meets future.', price=300, duration=6, image_url='https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&q=80', category='city', latitude=35.6762, longitude=139.6503, climate='Temperate', best_time_to_visit='Autumn'),
            Destination(name='Santorini', country='Greece', description='Dramatic views and sunsets.', price=250, duration=5, image_url='https://images.unsplash.com/photo-1613395877344-13d4c79e42d0?auto=format&fit=crop&q=80', category='luxury', latitude=36.3932, longitude=25.4615, climate='Mediterranean', best_time_to_visit='Summer'),
            Destination(name='New York', country='USA', description='The city that never sleeps.', price=280, duration=4, image_url='https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&q=80', category='city', latitude=40.7128, longitude=-74.0060, climate='Temperate', best_time_to_visit='Fall'),
            Destination(name='Rome', country='Italy', description='The Eternal City.', price=190, duration=6, image_url='https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&q=80', category='cultural', latitude=41.9028, longitude=12.4964, climate='Mediterranean', best_time_to_visit='Spring'),
            Destination(name='Cape Town', country='South Africa', description='Where ocean meets mountain.', price=170, duration=8, image_url='https://images.unsplash.com/photo-1580060839134-75a5edca2e99?auto=format&fit=crop&q=80', category='adventure', latitude=-33.9249, longitude=18.4241, climate='Mediterranean', best_time_to_visit='Summer'),
            Destination(name='Dubai', country='UAE', description='Ultramodern luxury.', price=350, duration=4, image_url='https://images.unsplash.com/photo-1512453979798-5ea90b7cadc9?auto=format&fit=crop&q=80', category='luxury', latitude=25.2048, longitude=55.2708, climate='Desert', best_time_to_visit='Winter')
        ]
        
        for d in destinations:
            existing = Destination.query.filter_by(name=d.name).first()
            if not existing:
                db.session.add(d)
        
        db.session.commit() # Commit to generate IDs
        
        # 2. Hotels
        paris = Destination.query.filter_by(name='Paris').first()
        bali = Destination.query.filter_by(name='Bali').first()
        tokyo = Destination.query.filter_by(name='Tokyo').first()
        dubai = Destination.query.filter_by(name='Dubai').first()

        hotels = [
            Hotel(name='The Ritz Paris', location='Paris, France', price=1200, rating=5.0, image_url='https://images.unsplash.com/photo-1566073771259-6a8506099945', destination_id=paris.id if paris else None, description='Legendary luxury in the heart of Paris.'),
            Hotel(name='Hotel Le Meurice', location='Paris, France', price=900, rating=4.9, image_url='https://images.unsplash.com/photo-1551882547-ff40c63fe5fa', destination_id=paris.id if paris else None, description='The embodiment of French elegance.'),
            Hotel(name='Ayana Resort', location='Bali, Indonesia', price=450, rating=4.8, image_url='https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9', destination_id=bali.id if bali else None, description='Clifftop luxury with sunset views.'),
            Hotel(name='Viceroy Bali', location='Bali, Indonesia', price=600, rating=4.9, image_url='https://images.unsplash.com/photo-1540541338287-41700207dee6', destination_id=bali.id if bali else None, description='Romantic jungle retreat.'),
            Hotel(name='Aman Tokyo', location='Tokyo, Japan', price=1100, rating=5.0, image_url='https://images.unsplash.com/photo-1618773928121-c32242e63f39', destination_id=tokyo.id if tokyo else None, description='Urban sanctuary high above the city.'),
            Hotel(name='Burj Al Arab', location='Dubai, UAE', price=2500, rating=5.0, image_url='https://images.unsplash.com/photo-1635548232958-812005086d1f', destination_id=dubai.id if dubai else None, description='The world\'s only 7-star hotel.')
        ]
        
        for h in hotels:
            db.session.add(h)

        # 3. Flights (Dynamic "Live" Data)
        now = datetime.now()
        flights = [
            Flight(airline='Emirates', origin='JFK (New York)', destination='DXB (Dubai)', price=1200, departure_time=now + timedelta(hours=2), duration='12h 30m', flight_number='EK201'),
            Flight(airline='Air France', origin='JFK (New York)', destination='CDG (Paris)', price=800, departure_time=now + timedelta(hours=5), duration='7h 20m', flight_number='AF007'),
            Flight(airline='JAL', origin='LAX (Los Angeles)', destination='HND (Tokyo)', price=1100, departure_time=now + timedelta(days=1, hours=10), duration='11h 45m', flight_number='JL061'),
            Flight(airline='Singapore Airlines', origin='LHR (London)', destination='SIN (Singapore)', price=950, departure_time=now + timedelta(hours=8), duration='13h 10m', flight_number='SQ308'),
            Flight(airline='Qatar Airways', origin='LHR (London)', destination='DOH (Doha)', price=850, departure_time=now + timedelta(hours=3), duration='6h 45m', flight_number='QR004'),
            Flight(airline='British Airways', origin='LHR (London)', destination='JFK (New York)', price=650, departure_time=now + timedelta(hours=4), duration='7h 55m', flight_number='BA117'),
            Flight(airline='Lufthansa', origin='FRA (Frankfurt)', destination='LHR (London)', price=200, departure_time=now + timedelta(hours=1), duration='1h 30m', flight_number='LH904'),
            Flight(airline='Delta', origin='ATL (Atlanta)', destination='LHR (London)', price=900, departure_time=now + timedelta(hours=6), duration='8h 15m', flight_number='DL030')
        ]
        
        for f in flights:
            db.session.add(f)
            
        db.session.commit()
        
        return jsonify({
            "message": "Database seeded successfully!",
            "destinations": Destination.query.count(),
            "hotels": Hotel.query.count(),
            "flights": Flight.query.count()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

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
