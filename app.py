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
