from werkzeug.security import generate_password_hash, check_password_hash
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


# Handle missing Pillow gracefully
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Warning: Pillow not available. Image optimization features disabled.")


# Stripe configuration (test keys)
# Use environment variables for Stripe keys
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

# Seeding Route
@app.route('/seed')
def seed_db():
    from new_models import Destination
    
    # Check if we already have data
    if Destination.query.first():
        return jsonify({"message": "Database already seeded", "count": Destination.query.count()})

    # Sample Data (Subset from add_destinations.py)
    new_destinations = [
        Destination(
            name='Paris', country='France', description='City of Light.', 
            price=200.0, duration=5, image_url='https://images.unsplash.com/photo-1502602898657-3e91760cbb34', 
            category='cultural', latitude=48.8566, longitude=2.3522, climate='Temperate', best_time_to_visit='Spring'
        ),
        Destination(
            name='Bali', country='Indonesia', description='Tropical paradise.', 
            price=150.0, duration=7, image_url='https://images.unsplash.com/photo-1537996194471-e657df975ab4', 
            category='beach', latitude=-8.4095, longitude=115.1889, climate='Tropical', best_time_to_visit='Summer'
        ),
        Destination(
            name='Tokyo', country='Japan', description='Modern bustling city.', 
            price=300.0, duration=6, image_url='https://images.unsplash.com/photo-1503899036084-c55cdd92da26', 
            category='city', latitude=35.6762, longitude=139.6503, climate='Temperate', best_time_to_visit='Autumn'
        ),
        Destination(
            name='New York', country='USA', description='The Big Apple.', 
            price=250.0, duration=4, image_url='https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9', 
            category='city', latitude=40.7128, longitude=-74.0060, climate='Temperate', best_time_to_visit='Fall'
        ),
        Destination(
            name='Santorini', country='Greece', description='Blue domes and sunsets.', 
            price=220.0, duration=5, image_url='https://images.unsplash.com/photo-1613395877344-13d4c79e42d0', 
            category='luxury', latitude=36.3932, longitude=25.4615, climate='Mediterranean', best_time_to_visit='Summer'
        ),
        Destination(
            name='Dubai', country='UAE', description='Luxury in the desert.', 
            price=400.0, duration=3, image_url='https://images.unsplash.com/photo-1512453979798-5ea90b7cadc9', 
            category='luxury', latitude=25.2048, longitude=55.2708, climate='Desert', best_time_to_visit='Winter'
        )
    ]
    
    for d in new_destinations:
        db.session.add(d)
        
    db.session.commit()
    return jsonify({"message": "Database seeded successfully!", "count": len(new_destinations)})


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


# Database connection pooling (only for non-SQLite databases)
if not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
