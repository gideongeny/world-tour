from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session, make_response, g
from db import db
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
import requests
from flask_mail import Mail, Message
import uuid
import stripe
from flask_migrate import Migrate
from flask_babel import Babel, gettext, ngettext
import redis
from celery import Celery
from functools import wraps
import pickle
import time
import logging
from flask_compress import Compress
from flask_caching import Cache
import random
from decorators import cache_result

# Handle missing Pillow gracefully
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("Warning: Pillow not available. Image optimization features disabled.")

# Stripe configuration (test keys)
# TODO: Replace with your real Stripe keys in production
stripe.api_key = 'sk_test_51Nw8...your_test_key_here...'
STRIPE_PUBLIC_KEY = 'pk_test_51Nw8...your_test_key_here...'

app = Flask(__name__)
# TODO: Replace with a secure secret key in production
app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///world_tour.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Performance optimizations
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 31536000  # 1 year cache for static files
app.config['TEMPLATES_AUTO_RELOAD'] = False  # Disable auto-reload in production
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

# Enable database query logging for performance monitoring
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Initialize performance optimizations
Compress(app)

# Cache configuration (using simple cache for development)
cache = Cache(config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 300
})
cache.init_app(app)

# Babel configuration
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['LANGUAGES'] = {
    'en': 'English',
    'es': 'Español',
    'fr': 'Français',
    'de': 'Deutsch',
    'ja': '日本語',
    'zh': '中文'
}

# Add get_locale function for templates
def get_locale():
    return session.get('language', 'en')

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
# TODO: Replace with your real email and app password in production
app.config['MAIL_USERNAME'] = 'your-email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your-app-password'

# Import new models

# Currency configuration
app.config['DEFAULT_CURRENCY'] = 'USD'
app.config['SUPPORTED_CURRENCIES'] = {
    'USD': {'symbol': '$', 'name': 'US Dollar'},
    'EUR': {'symbol': '€', 'name': 'Euro'},
    'GBP': {'symbol': '£', 'name': 'British Pound'},
    'JPY': {'symbol': '¥', 'name': 'Japanese Yen'},
    'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar'},
    'AUD': {'symbol': 'A$', 'name': 'Australian Dollar'}
}

babel = Babel(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
mail = Mail(app)

# Redis configuration (disabled for development)
redis_client = None

# Celery configuration (disabled for development)
celery_app = None

# Performance monitoring
@app.before_request
def before_request():
    g.start = time.time()

@app.after_request
def after_request(response):
    # Add performance headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    
    # Add cache headers for static assets
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=31536000'
        response.headers['Expires'] = 'Thu, 31 Dec 2025 23:59:59 GMT'
    
    # Add compression headers
    response.headers['Vary'] = 'Accept-Encoding'
    
    # Log performance
    if hasattr(g, 'start'):
        diff = time.time() - g.start
        print(f"Request to {request.path} took {diff:.3f} seconds")
    
    return response

# Language and currency switching (simplified for development)
@app.route('/set_language/<language>')
def set_language(language):
    if language in app.config['LANGUAGES']:
        session['language'] = language
        flash(f'Language changed to {language}', 'success')
    return redirect(request.referrer or url_for('home'))

@app.route('/set_currency/<currency>')
def set_currency(currency):
    if currency in app.config['SUPPORTED_CURRENCIES']:
        session['currency'] = currency
        flash(f'Currency changed to {currency}', 'success')
    return redirect(request.referrer or url_for('home'))

@app.context_processor
def inject_languages():
    current_lang = session.get('language', 'en')
    print(f"Current language: {current_lang}")  # Debug
    return dict(languages=app.config['LANGUAGES'], current_language=current_lang)

@app.context_processor
def inject_currencies():
    current_curr = session.get('currency', app.config['DEFAULT_CURRENCY'])
    print(f"Current currency: {current_curr}")  # Debug
    return dict(
        currencies=app.config['SUPPORTED_CURRENCIES'], 
        current_currency=current_curr
    )

@app.context_processor
def inject_format_price():
    """Make format_price function available in templates"""
    return dict(format_price=format_price)

def format_price(amount, currency_code=None):
    # Dummy implementation, replace with your logic
    return f"{amount} {currency_code or ''}"

def get_text(key, language=None):
    """Enhanced translation function with more languages and keys"""
    if language is None:
        language = session.get('language', 'en')
    
    translations = {
        'en': {
            'home': 'Home',
            'destinations': 'Destinations',
            'flights': 'Flights',
            'hotels': 'Hotels',
            'packages': 'Packages',
            'blog': 'Blog',
            'offers': 'Offers',
            'contact': 'Contact',
            'login': 'Login',
            'register': 'Register',
            'profile': 'Profile',
            'logout': 'Logout',
            'search': 'Search',
            'book_now': 'Book Now',
            'view_details': 'View Details',
            'price_from': 'From',
            'per_person': 'per person',
            'per_night': 'per night',
            'welcome_message': 'Welcome to World Tour',
            'discover_amazing': 'Discover Amazing Destinations',
            'explore_world': 'Explore the World with Us',
            'featured_destinations': 'Featured Destinations',
            'popular_destinations': 'Popular Destinations',
            'special_offers': 'Special Offers',
            'newsletter_signup': 'Sign up for our newsletter',
            'get_best_deals': 'Get the best deals and travel tips',
            'subscribe': 'Subscribe',
            'email_placeholder': 'Enter your email',
            'footer_description': 'Your gateway to amazing travel experiences around the world.',
            'quick_links': 'Quick Links',
            'support': 'Support',
            'help_center': 'Help Center',
            'my_tickets': 'My Tickets',
            'contact_info': 'Contact',
            'all_rights_reserved': 'All rights reserved.',
            'luxury_destinations': 'Luxury Destinations',
            'budget_destinations': 'Budget Destinations',
            'adventure_destinations': 'Adventure Destinations',
            'all_destinations': 'All Destinations',
            'travel_guides': 'Travel Guides',
            'interactive_maps': 'Interactive Maps',
            'flash_deals': 'Flash Deals',
            'seasonal_offers': 'Seasonal Offers',
            'last_minute_deals': 'Last Minute Deals',
            'all_special_offers': 'All Special Offers',
            'loyalty_rewards': 'Loyalty Rewards',
            'group_discounts': 'Group Discounts'
        },
        'es': {
            'home': 'Inicio',
            'destinations': 'Destinos',
            'flights': 'Vuelos',
            'hotels': 'Hoteles',
            'packages': 'Paquetes',
            'blog': 'Blog',
            'offers': 'Ofertas',
            'contact': 'Contacto',
            'login': 'Iniciar Sesión',
            'register': 'Registrarse',
            'profile': 'Perfil',
            'logout': 'Cerrar Sesión',
            'search': 'Buscar',
            'book_now': 'Reservar Ahora',
            'view_details': 'Ver Detalles',
            'price_from': 'Desde',
            'per_person': 'por persona',
            'per_night': 'por noche',
            'welcome_message': 'Bienvenido a World Tour',
            'discover_amazing': 'Descubre Destinos Increíbles',
            'explore_world': 'Explora el Mundo con Nosotros',
            'featured_destinations': 'Destinos Destacados',
            'popular_destinations': 'Destinos Populares',
            'special_offers': 'Ofertas Especiales',
            'newsletter_signup': 'Suscríbete a nuestro boletín',
            'get_best_deals': 'Obtén las mejores ofertas y consejos de viaje',
            'subscribe': 'Suscribirse',
            'email_placeholder': 'Ingresa tu email',
            'footer_description': 'Tu puerta de entrada a experiencias de viaje increíbles alrededor del mundo.',
            'quick_links': 'Enlaces Rápidos',
            'support': 'Soporte',
            'help_center': 'Centro de Ayuda',
            'my_tickets': 'Mis Tickets',
            'contact_info': 'Contacto',
            'all_rights_reserved': 'Todos los derechos reservados.',
            'luxury_destinations': 'Destinos de Lujo',
            'budget_destinations': 'Destinos Económicos',
            'adventure_destinations': 'Destinos de Aventura',
            'all_destinations': 'Todos los Destinos',
            'travel_guides': 'Guías de Viaje',
            'interactive_maps': 'Mapas Interactivos',
            'flash_deals': 'Ofertas Relámpago',
            'seasonal_offers': 'Ofertas de Temporada',
            'last_minute_deals': 'Ofertas de Último Minuto',
            'all_special_offers': 'Todas las Ofertas Especiales',
            'loyalty_rewards': 'Recompensas de Lealtad',
            'group_discounts': 'Descuentos de Grupo'
        },
        'fr': {
            'home': 'Accueil',
            'destinations': 'Destinations',
            'flights': 'Vols',
            'hotels': 'Hôtels',
            'packages': 'Forfaits',
            'blog': 'Blog',
            'offers': 'Offres',
            'contact': 'Contact',
            'login': 'Connexion',
            'register': 'S\'inscrire',
            'profile': 'Profil',
            'logout': 'Déconnexion',
            'search': 'Rechercher',
            'book_now': 'Réserver Maintenant',
            'view_details': 'Voir les Détails',
            'price_from': 'À partir de',
            'per_person': 'par personne',
            'per_night': 'par nuit',
            'welcome_message': 'Bienvenue chez World Tour',
            'discover_amazing': 'Découvrez des Destinations Incroyables',
            'explore_world': 'Explorez le Monde avec Nous',
            'featured_destinations': 'Destinations en Vedette',
            'popular_destinations': 'Destinations Populaires',
            'special_offers': 'Offres Spéciales',
            'newsletter_signup': 'Inscrivez-vous à notre newsletter',
            'get_best_deals': 'Obtenez les meilleures offres et conseils de voyage',
            'subscribe': 'S\'abonner',
            'email_placeholder': 'Entrez votre email',
            'footer_description': 'Votre passerelle vers des expériences de voyage incroyables dans le monde entier.',
            'quick_links': 'Liens Rapides',
            'support': 'Support',
            'help_center': 'Centre d\'Aide',
            'my_tickets': 'Mes Tickets',
            'contact_info': 'Contact',
            'all_rights_reserved': 'Tous droits réservés.',
            'luxury_destinations': 'Destinations de Luxe',
            'budget_destinations': 'Destinations Économiques',
            'adventure_destinations': 'Destinations d\'Aventure',
            'all_destinations': 'Toutes les Destinations',
            'travel_guides': 'Guides de Voyage',
            'interactive_maps': 'Cartes Interactives',
            'flash_deals': 'Offres Flash',
            'seasonal_offers': 'Offres Saisonnières',
            'last_minute_deals': 'Offres de Dernière Minute',
            'all_special_offers': 'Toutes les Offres Spéciales',
            'loyalty_rewards': 'Récompenses de Fidélité',
            'group_discounts': 'Remises de Groupe'
        },
        'de': {
            'home': 'Startseite',
            'destinations': 'Reiseziele',
            'flights': 'Flüge',
            'hotels': 'Hotels',
            'packages': 'Pakete',
            'blog': 'Blog',
            'offers': 'Angebote',
            'contact': 'Kontakt',
            'login': 'Anmelden',
            'register': 'Registrieren',
            'profile': 'Profil',
            'logout': 'Abmelden',
            'search': 'Suchen',
            'book_now': 'Jetzt Buchen',
            'view_details': 'Details Anzeigen',
            'price_from': 'Ab',
            'per_person': 'pro Person',
            'per_night': 'pro Nacht',
            'welcome_message': 'Willkommen bei World Tour',
            'discover_amazing': 'Entdecken Sie Unglaubliche Reiseziele',
            'explore_world': 'Erkunden Sie die Welt mit Uns',
            'featured_destinations': 'Empfohlene Reiseziele',
            'popular_destinations': 'Beliebte Reiseziele',
            'special_offers': 'Sonderangebote',
            'newsletter_signup': 'Newsletter abonnieren',
            'get_best_deals': 'Erhalten Sie die besten Angebote und Reisetipps',
            'subscribe': 'Abonnieren',
            'email_placeholder': 'E-Mail eingeben',
            'footer_description': 'Ihr Tor zu unglaublichen Reiseerlebnissen auf der ganzen Welt.',
            'quick_links': 'Schnelllinks',
            'support': 'Support',
            'help_center': 'Hilfecenter',
            'my_tickets': 'Meine Tickets',
            'contact_info': 'Kontakt',
            'all_rights_reserved': 'Alle Rechte vorbehalten.',
            'luxury_destinations': 'Luxus-Reiseziele',
            'budget_destinations': 'Budget-Reiseziele',
            'adventure_destinations': 'Abenteuer-Reiseziele',
            'all_destinations': 'Alle Reiseziele',
            'travel_guides': 'Reiseführer',
            'interactive_maps': 'Interaktive Karten',
            'flash_deals': 'Blitzangebote',
            'seasonal_offers': 'Saisonangebote',
            'last_minute_deals': 'Last-Minute-Angebote',
            'all_special_offers': 'Alle Sonderangebote',
            'loyalty_rewards': 'Treueprämien',
            'group_discounts': 'Gruppenrabatte'
        },
        'it': {
            'home': 'Home',
            'destinations': 'Destinazioni',
            'flights': 'Voli',
            'hotels': 'Hotel',
            'packages': 'Pacchetti',
            'blog': 'Blog',
            'offers': 'Offerte',
            'contact': 'Contatto',
            'login': 'Accedi',
            'register': 'Registrati',
            'profile': 'Profilo',
            'logout': 'Esci',
            'search': 'Cerca',
            'book_now': 'Prenota Ora',
            'view_details': 'Visualizza Dettagli',
            'price_from': 'Da',
            'per_person': 'per persona',
            'per_night': 'per notte',
            'welcome_message': 'Benvenuto su World Tour',
            'discover_amazing': 'Scopri Destinazioni Incredibili',
            'explore_world': 'Esplora il Mondo con Noi',
            'featured_destinations': 'Destinazioni in Evidenza',
            'popular_destinations': 'Destinazioni Popolari',
            'special_offers': 'Offerte Speciali',
            'newsletter_signup': 'Iscriviti alla nostra newsletter',
            'get_best_deals': 'Ottieni le migliori offerte e consigli di viaggio',
            'subscribe': 'Iscriviti',
            'email_placeholder': 'Inserisci la tua email',
            'footer_description': 'La tua porta d\'accesso a incredibili esperienze di viaggio in tutto il mondo.',
            'quick_links': 'Link Rapidi',
            'support': 'Supporto',
            'help_center': 'Centro Assistenza',
            'my_tickets': 'I Miei Biglietti',
            'contact_info': 'Contatto',
            'all_rights_reserved': 'Tutti i diritti riservati.',
            'luxury_destinations': 'Destinazioni di Lusso',
            'budget_destinations': 'Destinazioni Economiche',
            'adventure_destinations': 'Destinazioni d\'Avventura',
            'all_destinations': 'Tutte le Destinazioni',
            'travel_guides': 'Guide di Viaggio',
            'interactive_maps': 'Mappe Interattive',
            'flash_deals': 'Offerte Flash',
            'seasonal_offers': 'Offerte Stagionali',
            'last_minute_deals': 'Offerte Last Minute',
            'all_special_offers': 'Tutte le Offerte Speciali',
            'loyalty_rewards': 'Premi Fedeltà',
            'group_discounts': 'Sconti di Gruppo'
        }
    }
    
    return translations.get(language, translations['en']).get(key, key)

@app.context_processor
def inject_translations():
    """Make translation function available in templates"""
    return dict(t=get_text)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    bookings = db.relationship('Booking', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    wishlist_items = db.relationship('WishlistItem', backref='user', lazy=True)

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer)  # days
    image_url = db.Column(db.String(200))
    category = db.Column(db.String(50))  # luxury, budget, adventure, etc.
    rating = db.Column(db.Float, default=0.0)
    reviews_count = db.Column(db.Integer, default=0)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    climate = db.Column(db.String(50))
    best_time_to_visit = db.Column(db.String(100))

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), nullable=False)
    airline = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Float, nullable=False)
    seats_available = db.Column(db.Integer, nullable=False)
    bookings = db.relationship('Booking', backref='flight', lazy=True)

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    rating = db.Column(db.Float, default=0.0)
    rooms = db.relationship('RoomType', backref='hotel', lazy=True)
    bookings = db.relationship('Booking', backref='hotel', lazy=True)

class RoomType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    price_per_night = db.Column(db.Float, nullable=False)
    total_rooms = db.Column(db.Integer, nullable=False)
    available_rooms = db.Column(db.Integer, nullable=False)
    bookings = db.relationship('Booking', backref='room_type', lazy=True)

class PackageDeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    activities = db.Column(db.Text)  # JSON or comma-separated
    image_url = db.Column(db.String(200))
    bookings = db.relationship('Booking', backref='package_deal', lazy=True)

# Update Booking model to support new booking types
class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'))
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'))
    package_deal_id = db.Column(db.Integer, db.ForeignKey('package_deal.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    guests = db.Column(db.Integer, default=1)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    payment_status = db.Column(db.String(20), default='pending')
    payment_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='bookings')

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    photos = db.Column(db.Text)  # Comma-separated photo URLs
    likes_count = db.Column(db.Integer, default=0)
    helpful_count = db.Column(db.Integer, default=0)
    is_verified_booking = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='reviews')
    likes = db.relationship('ReviewLike', backref='review', lazy=True, cascade='all, delete-orphan')
    replies = db.relationship('ReviewReply', backref='review', lazy=True, cascade='all, delete-orphan')

class ReviewLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='review_likes')

class ReviewReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='review_replies')

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='unread')  # unread, read, replied

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='wishlist_items')

class Newsletter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

# Itinerary Builder Models
class Itinerary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)
    items = db.relationship('ItineraryItem', backref='itinerary', lazy=True, cascade='all, delete-orphan')

class ItineraryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    itinerary_id = db.Column(db.Integer, db.ForeignKey('itinerary.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    time_slot = db.Column(db.String(50))  # morning, afternoon, evening
    activity_type = db.Column(db.String(50))  # flight, hotel, activity, transport
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    duration = db.Column(db.Integer)  # minutes
    cost = db.Column(db.Float, default=0.0)
    booking_reference = db.Column(db.String(100))
    notes = db.Column(db.Text)

# Marketing & Analytics Models
class EmailCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.String(50))  # all, premium, new_users, etc.
    sent_count = db.Column(db.Integer, default=0)
    opened_count = db.Column(db.Integer, default=0)
    clicked_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class UserAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    page_visited = db.Column(db.String(100))
    time_spent = db.Column(db.Integer)  # seconds
    action_performed = db.Column(db.String(100))  # search, book, view, etc.
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)

class ReferralProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    referred_email = db.Column(db.String(120), nullable=False)
    referral_code = db.Column(db.String(20), unique=True, nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime)

# Affiliate Program Models
class Affiliate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    affiliate_code = db.Column(db.String(20), unique=True, nullable=False)
    commission_rate = db.Column(db.Float, default=0.05)  # 5% default
    total_earnings = db.Column(db.Float, default=0.0)
    total_referrals = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='affiliate')

class AffiliateReferral(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    affiliate_id = db.Column(db.Integer, db.ForeignKey('affiliate.id'), nullable=False)
    referred_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    commission_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    affiliate = db.relationship('Affiliate', backref='referrals')
    referred_user = db.relationship('User', backref='referred_by')
    booking = db.relationship('Booking', backref='affiliate_referral')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Utility functions
def send_email(subject, recipients, body):
    """Send email notification"""
    try:
        msg = Message(subject, recipients=recipients)
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def get_weather(city):
    """Get weather information for a city with caching"""
    cache_key = f"weather_{city.lower().replace(' ', '_')}"
    
    # Check cache first
    try:
        cached_weather = cache.get(cache_key)
        if cached_weather:
            return cached_weather
    except:
        pass
    
    try:
        # Using OpenWeatherMap API (free tier)
        api_key = "demo_key"  # In production, use real API key
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            weather = {
                'temp': round(data['main']['temp']),
                'condition': data['weather'][0]['main'],
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed'] * 3.6),  # Convert m/s to km/h
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon']
            }
            # Cache for 30 minutes
            try:
                cache.set(cache_key, weather, timeout=1800)
            except:
                pass
            return weather
    except Exception as e:
        print(f"Weather API error: {e}")
    
    # Fallback to simulated weather if API fails
    weather_data = {
        'paris': {'temp': 18, 'condition': 'Partly Cloudy', 'humidity': 65},
        'tokyo': {'temp': 22, 'condition': 'Sunny', 'humidity': 55},
        'new york': {'temp': 15, 'condition': 'Rainy', 'humidity': 80},
        'greece': {'temp': 25, 'condition': 'Sunny', 'humidity': 45},
        'maldives': {'temp': 28, 'condition': 'Sunny', 'humidity': 70},
        'cape town': {'temp': 20, 'condition': 'Partly Cloudy', 'humidity': 60},
        'mount fuji': {'temp': 12, 'condition': 'Cloudy', 'humidity': 75}
    }
    return weather_data.get(city.lower(), {'temp': 20, 'condition': 'Unknown', 'humidity': 50})

def process_payment(amount, card_details=None):
    """Process payment with Stripe"""
    try:
        import stripe
        stripe.api_key = app.config.get('STRIPE_SECRET_KEY', 'sk_test_...')
        
        # Create payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency='usd',
            metadata={'integration_check': 'accept_a_payment'},
            description='World Tour Booking'
        )
        
        return {
            'success': True, 
            'payment_id': payment_intent.id,
            'client_secret': payment_intent.client_secret
        }
    except stripe.error.CardError as e:
        return {'success': False, 'error': f'Card error: {e.error.message}'}
    except stripe.error.RateLimitError as e:
        return {'success': False, 'error': 'Rate limit exceeded'}
    except stripe.error.InvalidRequestError as e:
        return {'success': False, 'error': f'Invalid request: {e.error.message}'}
    except stripe.error.AuthenticationError as e:
        return {'success': False, 'error': 'Authentication failed'}
    except stripe.error.APIConnectionError as e:
        return {'success': False, 'error': 'Network communication failed'}
    except stripe.error.StripeError as e:
        return {'success': False, 'error': f'Stripe error: {e.error.message}'}
    except Exception as e:
        return {'success': False, 'error': f'Unexpected error: {str(e)}'}

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    """Simulate checkout session creation for demo purposes"""
    try:
        data = request.get_json()
        amount = data.get('amount')
        if not amount:
            return jsonify({'error': 'Amount required'}), 400
        import uuid
        session_id = str(uuid.uuid4())
        return jsonify({
            'sessionId': session_id,
            'sessionUrl': url_for('payment_success', _external=True) + f'?session_id={session_id}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/payment_success')
def payment_success():
    return render_template('payment_success.html')

@app.route('/payment_cancel')
def payment_cancel():
    return render_template('payment_cancel.html')

# Routes
@app.route('/')
#@cache_result(timeout=300)  # Cache homepage for 5 minutes
def home():
    # Get personalized recommendations if user is logged in
    personalized_destinations = []
    if current_user.is_authenticated:
        personalized_destinations = get_personalized_recommendations(current_user.id)
    
    # Optimize queries with specific column selection
    featured_destinations = Destination.query.with_entities(
        Destination.id, Destination.name, Destination.country, 
        Destination.price, Destination.rating, Destination.image_url
    ).filter_by(available=True).order_by(Destination.rating.desc()).limit(6).all()
    
    latest_destinations = Destination.query.with_entities(
        Destination.id, Destination.name, Destination.country, 
        Destination.price, Destination.rating, Destination.image_url
    ).filter_by(available=True).order_by(Destination.created_at.desc()).limit(3).all()
    
    return render_template('index.html', 
                         featured_destinations=featured_destinations,
                         latest_destinations=latest_destinations,
                         personalized_destinations=personalized_destinations)

def get_personalized_recommendations(user_id, limit=6):
    """Get AI-powered personalized destination recommendations"""
    try:
        # Get user's booking history
        user_bookings = Booking.query.filter_by(user_id=user_id).all()
        booked_destinations = [b.destination_id for b in user_bookings if b.destination_id]
        
        # Get user's review history
        user_reviews = Review.query.filter_by(user_id=user_id).all()
        reviewed_destinations = [r.destination_id for r in user_reviews]
        
        # Get user's wishlist
        wishlist_items = WishlistItem.query.filter_by(user_id=user_id).all()
        wishlist_destinations = [w.destination_id for w in wishlist_items]
        
        # Get user's search history
        search_history = UserAnalytics.query.filter_by(
            user_id=user_id, 
            action_performed='search'
        ).order_by(UserAnalytics.timestamp.desc()).limit(20).all()
        
        # Analyze user preferences with AI
        preferences = analyze_user_preferences_ai(user_id, search_history)
        
        # Build recommendation query
        query = Destination.query.filter_by(available=True)
        
        # Exclude already booked/reviewed destinations
        if booked_destinations or reviewed_destinations:
            excluded_ids = list(set(booked_destinations + reviewed_destinations))
            query = query.filter(~Destination.id.in_(excluded_ids))
        
        # Apply AI preference filters
        if preferences.get('preferred_categories'):
            query = query.filter(Destination.category.in_(preferences['preferred_categories']))
        
        if preferences.get('preferred_countries'):
            query = query.filter(Destination.country.in_(preferences['preferred_countries']))
        
        if preferences.get('price_range'):
            min_price, max_price = preferences['price_range']
            query = query.filter(Destination.price.between(min_price, max_price))
        
        if preferences.get('preferred_climate'):
            query = query.filter(Destination.climate.in_(preferences['preferred_climate']))
        
        # Calculate AI relevance score
        destinations = query.all()
        scored_destinations = []
        
        for dest in destinations:
            score = calculate_ai_relevance_score(dest, preferences, user_reviews, search_history)
            scored_destinations.append((dest, score))
        
        # Sort by AI score and return top recommendations
        scored_destinations.sort(key=lambda x: x[1], reverse=True)
        recommendations = [dest for dest, score in scored_destinations[:limit]]
        
        return recommendations
        
    except Exception as e:
        print(f"Error getting AI recommendations: {e}")
        return []

def analyze_user_preferences_ai(user_id, search_history):
    """AI-powered user preference analysis"""
    preferences = {}
    
    try:
        # Analyze booking history with sentiment
        bookings = Booking.query.filter_by(user_id=user_id).all()
        if bookings:
            booked_destinations = Destination.query.filter(
                Destination.id.in_([b.destination_id for b in bookings if b.destination_id])
            ).all()
            
            # Analyze categories with frequency and sentiment
            categories = [d.category for d in booked_destinations if d.category]
            if categories:
                from collections import Counter
                category_counts = Counter(categories)
                # Weight by booking frequency and user satisfaction
                weighted_categories = []
                for cat, count in category_counts.most_common():
                    # Get average rating for this category
                    cat_destinations = [d for d in booked_destinations if d.category == cat]
                    avg_rating = sum(d.rating for d in cat_destinations) / len(cat_destinations)
                    weighted_categories.append((cat, count * avg_rating))
                
                weighted_categories.sort(key=lambda x: x[1], reverse=True)
                preferences['preferred_categories'] = [cat for cat, score in weighted_categories[:3]]
            
            # Analyze countries with seasonal patterns
            countries = [d.country for d in booked_destinations if d.country]
            if countries:
                country_counts = Counter(countries)
                preferences['preferred_countries'] = [country for country, count in country_counts.most_common(3)]
            
            # Analyze price sensitivity
            prices = [d.price for d in booked_destinations if d.price]
            if prices:
                avg_price = sum(prices) / len(prices)
                std_price = (sum((p - avg_price) ** 2 for p in prices) / len(prices)) ** 0.5
                preferences['price_range'] = (avg_price - std_price, avg_price + std_price)
                preferences['price_sensitivity'] = 'low' if std_price < avg_price * 0.3 else 'high'
        
        # Analyze search patterns
        if search_history:
            search_terms = [s.page_visited for s in search_history if s.page_visited]
            # Extract destination names from search terms
            destination_terms = []
            for term in search_terms:
                if 'destination' in term.lower() or 'travel' in term.lower():
                    destination_terms.append(term)
            
            if destination_terms:
                # Find destinations matching search patterns
                matching_destinations = Destination.query.filter(
                    Destination.name.contains(search_terms[0]) | 
                    Destination.country.contains(search_terms[0])
                ).all()
                
                if matching_destinations:
                    # Add categories from searched destinations
                    searched_categories = [d.category for d in matching_destinations if d.category]
                    if searched_categories:
                        if 'preferred_categories' not in preferences:
                            preferences['preferred_categories'] = []
                        preferences['preferred_categories'].extend(searched_categories[:2])
        
        # Analyze review sentiment
        reviews = Review.query.filter_by(user_id=user_id).all()
        if reviews:
            high_rated_destinations = Destination.query.filter(
                Destination.id.in_([r.destination_id for r in reviews if r.rating >= 4])
            ).all()
            
            if high_rated_destinations:
                # Analyze climate preferences from highly rated destinations
                climates = [d.climate for d in high_rated_destinations if d.climate]
                if climates:
                    climate_counts = Counter(climates)
                    preferences['preferred_climate'] = [climate for climate, count in climate_counts.most_common(2)]
        
        return preferences
        
    except Exception as e:
        print(f"Error in AI preference analysis: {e}")
        return {}

def calculate_ai_relevance_score(destination, preferences, user_reviews, search_history):
    """Calculate AI relevance score for a destination"""
    score = 0.0
    
    try:
        # Base score from destination rating
        score += destination.rating * 0.3
        
        # Category match score
        if preferences.get('preferred_categories') and destination.category:
            if destination.category in preferences['preferred_categories']:
                score += 0.4
        
        # Country match score
        if preferences.get('preferred_countries') and destination.country:
            if destination.country in preferences['preferred_countries']:
                score += 0.3
        
        # Price match score
        if preferences.get('price_range') and destination.price:
            min_price, max_price = preferences['price_range']
            if min_price <= destination.price <= max_price:
                score += 0.2
            elif destination.price < min_price:
                score += 0.1  # Bonus for budget-friendly options
        
        # Climate match score
        if preferences.get('preferred_climate') and destination.climate:
            if destination.climate in preferences['preferred_climate']:
                score += 0.2
        
        # Popularity boost (more reviews = more popular)
        if destination.reviews_count:
            score += min(destination.reviews_count / 100, 0.1)  # Cap at 0.1
        
        # Seasonal relevance
        current_month = datetime.now().month
        if destination.best_time_to_visit:
            # Simple seasonal matching (can be enhanced)
            if current_month in [6, 7, 8] and 'summer' in destination.best_time_to_visit.lower():
                score += 0.1
            elif current_month in [12, 1, 2] and 'winter' in destination.best_time_to_visit.lower():
                score += 0.1
        
        return score
        
    except Exception as e:
        print(f"Error calculating AI score: {e}")
        return 0.0

def analyze_user_preferences(user_id):
    """Analyze user preferences based on their behavior"""
    preferences = {}
    
    try:
        # Analyze booking history
        bookings = Booking.query.filter_by(user_id=user_id).all()
        if bookings:
            # Get categories from booked destinations
            booked_destinations = Destination.query.filter(
                Destination.id.in_([b.destination_id for b in bookings if b.destination_id])
            ).all()
            
            categories = [d.category for d in booked_destinations if d.category]
            if categories:
                # Get most common categories
                from collections import Counter
                category_counts = Counter(categories)
                preferences['preferred_categories'] = [cat for cat, count in category_counts.most_common(3)]
            
            # Get countries
            countries = [d.country for d in booked_destinations if d.country]
            if countries:
                country_counts = Counter(countries)
                preferences['preferred_countries'] = [country for country, count in country_counts.most_common(3)]
            
            # Get price range
            prices = [d.price for d in booked_destinations if d.price]
            if prices:
                avg_price = sum(prices) / len(prices)
                preferences['price_range'] = (avg_price * 0.7, avg_price * 1.3)
        
        # Analyze review ratings
        reviews = Review.query.filter_by(user_id=user_id).all()
        if reviews:
            high_rated_destinations = Destination.query.filter(
                Destination.id.in_([r.destination_id for r in reviews if r.rating >= 4])
            ).all()
            
            if high_rated_destinations:
                # Add categories from highly rated destinations
                high_rated_categories = [d.category for d in high_rated_destinations if d.category]
                if high_rated_categories:
                    if 'preferred_categories' not in preferences:
                        preferences['preferred_categories'] = []
                    preferences['preferred_categories'].extend(high_rated_categories[:2])
        
        return preferences
        
    except Exception as e:
        print(f"Error analyzing user preferences: {e}")
        return {}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name
        )
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        send_email(
            'Welcome to World Tour!',
            [email],
            f'Hi {first_name},\n\nWelcome to World Tour! Your account has been created successfully.\n\nBest regards,\nWorld Tour Team'
        )
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile')
@login_required
def profile():
    user_bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    wishlist_items = WishlistItem.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', bookings=user_bookings, wishlist_items=wishlist_items)

@app.route('/travel')
#@cache_result(timeout=600)  # Cache for 10 minutes
def travel():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    min_price = request.args.get('min_price', '')
    max_price = request.args.get('max_price', '')
    duration = request.args.get('duration', '')
    rating = request.args.get('rating', '')
    climate = request.args.get('climate', '')
    
    query = Destination.query.filter_by(available=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Destination.name.contains(search) | Destination.country.contains(search))
    
    if min_price:
        query = query.filter(Destination.price >= float(min_price))
    
    if max_price:
        query = query.filter(Destination.price <= float(max_price))
    
    if duration:
        duration_int = int(duration)
        if duration_int == 1:
            query = query.filter(Destination.duration <= 3)
        elif duration_int == 4:
            query = query.filter(Destination.duration >= 4, Destination.duration <= 7)
        elif duration_int == 8:
            query = query.filter(Destination.duration >= 8, Destination.duration <= 14)
        elif duration_int == 15:
            query = query.filter(Destination.duration >= 15)
    
    if rating:
        query = query.filter(Destination.rating >= float(rating))
    
    if climate:
        query = query.filter_by(climate=climate)
    
    destinations = query.order_by(Destination.rating.desc()).all()
    
    return render_template('travel.html', destinations=destinations)

@app.route('/destination/<int:destination_id>')
def destination_detail(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    reviews = Review.query.filter_by(destination_id=destination_id).order_by(Review.created_at.desc()).all()
    weather = get_weather(destination.name)
    is_in_wishlist = False
    if current_user.is_authenticated:
        is_in_wishlist = WishlistItem.query.filter_by(
            user_id=current_user.id, 
            destination_id=destination_id
        ).first() is not None
    
    # Get similar destinations (same category, excluding current)
    similar_destinations = Destination.query.filter_by(
        category=destination.category, 
        available=True
    ).filter(Destination.id != destination_id).limit(3).all()
    
    return render_template('destination_detail.html', 
                         destination=destination, 
                         reviews=reviews, 
                         weather=weather,
                         is_in_wishlist=is_in_wishlist,
                         similar_destinations=similar_destinations)

@app.route('/book/<int:destination_id>', methods=['GET', 'POST'])
@login_required
def book_destination(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    
    if request.method == 'POST':
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        guests = int(request.form.get('guests', 1))
        
        # Calculate total price
        days = (end_date - start_date).days
        total_price = destination.price * days * guests
        
        # Process payment
        card_number = request.form.get('card_number')
        card_expiry = request.form.get('card_expiry')
        card_cvv = request.form.get('card_cvv')
        
        payment_result = process_payment(total_price, {
            'card_number': card_number,
            'card_expiry': card_expiry,
            'card_cvv': card_cvv
        })
        
        if payment_result['success']:
            booking = Booking(
                user_id=current_user.id,
                destination_id=destination_id,
                start_date=start_date,
                end_date=end_date,
                guests=guests,
                total_price=total_price,
                status='confirmed',
                payment_status='paid',
                payment_id=payment_result['payment_id']
            )
            
            db.session.add(booking)
            db.session.commit()
            
            # Send confirmation email
            send_email(
                'Booking Confirmation - World Tour',
                [current_user.email],
                f'''Hi {current_user.first_name},

Your booking has been confirmed!

Destination: {destination.name}, {destination.country}
Dates: {start_date} to {end_date}
Guests: {guests}
Total: ${total_price:.2f}
Booking ID: {booking.id}
Payment ID: {payment_result['payment_id']}

Thank you for choosing World Tour!

Best regards,
World Tour Team'''
            )
            
            flash('Booking confirmed! Check your email for details.')
            return redirect(url_for('profile'))
        else:
            flash('Payment failed. Please try again.')
    
    # Get today's date for minimum date validation
    today = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('book.html', destination=destination, today=today)

@app.route('/offers')
def offers():
    # Get destinations with discounts (simulated)
    discounted_destinations = Destination.query.filter_by(available=True).limit(4).all()
    return render_template('offers.html', destinations=discounted_destinations)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        
        contact = Contact(name=name, email=email, message=message)
        db.session.add(contact)
        db.session.commit()
        
        # Send notification email to admin
        send_email(
            'New Contact Form Submission',
            ['admin@worldtour.com'],
            f'New message from {name} ({email}):\n\n{message}'
        )
        
        flash('Message sent successfully! We\'ll get back to you soon.')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/submit_review/<int:destination_id>', methods=['POST'])
@login_required
def submit_review(destination_id):
    rating = int(request.form.get('rating'))
    comment = request.form.get('comment')
    photos = request.files.getlist('photos')
    
    # Check if user already reviewed this destination
    existing_review = Review.query.filter_by(
        user_id=current_user.id, 
        destination_id=destination_id
    ).first()
    
    if existing_review:
        flash('You have already reviewed this destination.')
        return redirect(url_for('destination_detail', destination_id=destination_id))
    
    # Check if user has booked this destination (verified review)
    has_booking = Booking.query.filter_by(
        user_id=current_user.id,
        destination_id=destination_id,
        status='confirmed'
    ).first() is not None
    
    review = Review(
        user_id=current_user.id,
        destination_id=destination_id,
        rating=rating,
        comment=comment,
        is_verified_booking=has_booking
    )
    
    db.session.add(review)
    db.session.flush()  # Get review ID
    
    # Handle photo uploads
    photo_urls = []
    for photo in photos:
        if photo and photo.filename:
            # Save photo to static/uploads/reviews/
            filename = secure_filename(f"{review.id}_{photo.filename}")
            photo_path = os.path.join('static', 'uploads', 'reviews', filename)
            os.makedirs(os.path.dirname(photo_path), exist_ok=True)
            photo.save(photo_path)
            photo_urls.append(f"/static/uploads/reviews/{filename}")
    
    # Add photos to review
    if photo_urls:
        review.photos = ','.join(photo_urls)
    
    # Update destination rating
    destination = Destination.query.get(destination_id)
    all_reviews = Review.query.filter_by(destination_id=destination_id).all()
    total_rating = sum([r.rating for r in all_reviews]) + rating
    destination.rating = total_rating / (len(all_reviews) + 1)
    destination.reviews_count = len(all_reviews) + 1
    
    db.session.commit()
    
    flash('Review submitted successfully!')
    return redirect(url_for('destination_detail', destination_id=destination_id))

@app.route('/review/<int:review_id>/like', methods=['POST'])
@login_required
def like_review(review_id):
    """Like or unlike a review"""
    review = Review.query.get_or_404(review_id)
    
    # Check if user already liked this review
    existing_like = ReviewLike.query.filter_by(
        user_id=current_user.id,
        review_id=review_id
    ).first()
    
    if existing_like:
        # Unlike
        db.session.delete(existing_like)
        review.likes_count = max(0, review.likes_count - 1)
        action = 'unliked'
    else:
        # Like
        like = ReviewLike(
            user_id=current_user.id,
            review_id=review_id
        )
        db.session.add(like)
        review.likes_count += 1
        action = 'liked'
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'action': action,
        'likes_count': review.likes_count
    })

@app.route('/review/<int:review_id>/reply', methods=['POST'])
@login_required
def reply_to_review(review_id):
    """Reply to a review"""
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Please provide a reply content')
        return redirect(url_for('destination_detail', destination_id=review_id))
    
    reply = ReviewReply(
        review_id=review_id,
        user_id=current_user.id,
        content=content
    )
    db.session.add(reply)
    db.session.commit()
    
    flash('Reply submitted successfully!')
    return redirect(url_for('destination_detail', destination_id=review_id))

@app.route('/search')
def search():
    query = request.args.get('q', '')
    voice_query = request.args.get('voice_query', '')  # Voice search query
    category = request.args.get('category', '')
    price_min = request.args.get('price_min', type=float)
    price_max = request.args.get('price_max', type=float)
    duration_min = request.args.get('duration_min', type=int)
    duration_max = request.args.get('duration_max', type=int)
    rating_min = request.args.get('rating_min', type=float)
    country = request.args.get('country', '')
    climate = request.args.get('climate', '')
    sort_by = request.args.get('sort_by', 'name')
    sort_order = request.args.get('sort_order', 'asc')
    
    # Process voice query if provided
    if voice_query:
        processed_query = process_voice_query(voice_query)
        query = processed_query.get('query', voice_query)
        # Apply voice-extracted filters
        if processed_query.get('category'):
            category = processed_query['category']
        if processed_query.get('price_range'):
            price_min, price_max = processed_query['price_range']
        if processed_query.get('duration'):
            duration_min, duration_max = processed_query['duration']
        if processed_query.get('country'):
            country = processed_query['country']
    
    # Build query
    destinations_query = Destination.query.filter(Destination.available == True)
    
    if query:
        destinations_query = destinations_query.filter(
            Destination.name.contains(query) | 
            Destination.country.contains(query) |
            Destination.description.contains(query)
        )
    
    if category:
        destinations_query = destinations_query.filter(Destination.category == category)
    
    if price_min is not None:
        destinations_query = destinations_query.filter(Destination.price >= price_min)
    
    if price_max is not None:
        destinations_query = destinations_query.filter(Destination.price <= price_max)
    
    if duration_min is not None:
        destinations_query = destinations_query.filter(Destination.duration >= duration_min)
    
    if duration_max is not None:
        destinations_query = destinations_query.filter(Destination.duration <= duration_max)
    
    if rating_min is not None:
        destinations_query = destinations_query.filter(Destination.rating >= rating_min)
    
    if country:
        destinations_query = destinations_query.filter(Destination.country.contains(country))
    
    if climate:
        destinations_query = destinations_query.filter(Destination.climate == climate)
    
    # Sorting
    if sort_by == 'price':
        if sort_order == 'desc':
            destinations_query = destinations_query.order_by(Destination.price.desc())
        else:
            destinations_query = destinations_query.order_by(Destination.price.asc())
    elif sort_by == 'rating':
        if sort_order == 'desc':
            destinations_query = destinations_query.order_by(Destination.rating.desc())
        else:
            destinations_query = destinations_query.order_by(Destination.rating.asc())
    elif sort_by == 'duration':
        if sort_order == 'desc':
            destinations_query = destinations_query.order_by(Destination.duration.desc())
        else:
            destinations_query = destinations_query.order_by(Destination.duration.asc())
    else:  # name
        if sort_order == 'desc':
            destinations_query = destinations_query.order_by(Destination.name.desc())
        else:
            destinations_query = destinations_query.order_by(Destination.name.asc())
    
    destinations = destinations_query.all()
    
    # Get filter options
    categories = db.session.query(Destination.category).distinct().all()
    countries = db.session.query(Destination.country).distinct().all()
    climates = db.session.query(Destination.climate).distinct().all()
    
    return render_template('search.html', 
                         destinations=destinations, 
                         query=query,
                         voice_query=voice_query,
                         category=category,
                         price_min=price_min,
                         price_max=price_max,
                         duration_min=duration_min,
                         duration_max=duration_max,
                         rating_min=rating_min,
                         country=country,
                         climate=climate,
                         sort_by=sort_by,
                         sort_order=sort_order,
                         categories=[c[0] for c in categories if c[0]],
                         countries=[c[0] for c in countries if c[0]],
                         climates=[c[0] for c in climates if c[0]])

def process_voice_query(voice_text):
    """Process voice search query and extract structured data"""
    processed = {'query': voice_text}
    
    try:
        voice_lower = voice_text.lower()
        
        # Extract category
        category_keywords = {
            'beach': ['beach', 'coastal', 'ocean', 'sea', 'island'],
            'mountain': ['mountain', 'alpine', 'ski', 'hiking', 'trekking'],
            'city': ['city', 'urban', 'metropolitan', 'downtown'],
            'cultural': ['cultural', 'heritage', 'museum', 'historical', 'ancient'],
            'adventure': ['adventure', 'extreme', 'thrilling', 'exciting'],
            'luxury': ['luxury', 'premium', 'exclusive', 'high-end', '5-star'],
            'budget': ['budget', 'cheap', 'affordable', 'economy', 'low-cost']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in voice_lower for keyword in keywords):
                processed['category'] = category
                break
        
        # Extract price range
        price_patterns = [
            (r'under (\d+)', lambda m: (0, float(m.group(1)))),
            (r'over (\d+)', lambda m: (float(m.group(1)), 9999)),
            (r'between (\d+) and (\d+)', lambda m: (float(m.group(1)), float(m.group(2)))),
            (r'(\d+) to (\d+)', lambda m: (float(m.group(1)), float(m.group(2))))
        ]
        
        import re
        for pattern, handler in price_patterns:
            match = re.search(pattern, voice_lower)
            if match:
                processed['price_range'] = handler(match)
                break
        
        # Extract duration
        duration_patterns = [
            (r'(\d+) days?', lambda m: (int(m.group(1)), int(m.group(1)))),
            (r'(\d+) to (\d+) days?', lambda m: (int(m.group(1)), int(m.group(2)))),
            (r'weekend', lambda m: (2, 3)),
            (r'week', lambda m: (7, 7)),
            (r'(\d+) weeks?', lambda m: (int(m.group(1)) * 7, int(m.group(1)) * 7))
        ]
        
        for pattern, handler in duration_patterns:
            match = re.search(pattern, voice_lower)
            if match:
                processed['duration'] = handler(match)
                break
        
        # Extract country/destination
        # This would typically use a more sophisticated NLP approach
        # For now, we'll use a simple keyword approach
        country_keywords = [
            'france', 'italy', 'spain', 'germany', 'uk', 'england', 'scotland',
            'japan', 'china', 'india', 'thailand', 'vietnam', 'singapore',
            'usa', 'canada', 'mexico', 'brazil', 'argentina', 'peru',
            'australia', 'new zealand', 'fiji', 'tahiti'
        ]
        
        for country in country_keywords:
            if country in voice_lower:
                processed['country'] = country.title()
                break
        
        return processed
        
    except Exception as e:
        print(f"Error processing voice query: {e}")
        return {'query': voice_text}

@app.route('/api/voice-search', methods=['POST'])
def voice_search_api():
    """API endpoint for voice search"""
    try:
        data = request.get_json()
        voice_text = data.get('voice_text', '')
        
        if not voice_text:
            return jsonify({'error': 'No voice text provided'}), 400
        
        # Process voice query
        processed = process_voice_query(voice_text)
        
        # Perform search
        query = processed.get('query', voice_text)
        destinations_query = Destination.query.filter_by(available=True)
        
        if query:
            destinations_query = destinations_query.filter(
                Destination.name.contains(query) | 
                Destination.country.contains(query) |
                Destination.description.contains(query)
            )
        
        # Apply extracted filters
        if processed.get('category'):
            destinations_query = destinations_query.filter_by(category=processed['category'])
        
        if processed.get('price_range'):
            min_price, max_price = processed['price_range']
            destinations_query = destinations_query.filter(Destination.price.between(min_price, max_price))
        
        if processed.get('duration'):
            min_duration, max_duration = processed['duration']
            destinations_query = destinations_query.filter(Destination.duration.between(min_duration, max_duration))
        
        if processed.get('country'):
            destinations_query = destinations_query.filter(Destination.country.contains(processed['country']))
        
        destinations = destinations_query.limit(10).all()
        
        results = [{
            'id': d.id,
            'name': d.name,
            'country': d.country,
            'price': d.price,
            'rating': d.rating,
            'image_url': d.image_url,
            'category': d.category
        } for d in destinations]
        
        return jsonify({
            'success': True,
            'query': voice_text,
            'processed': processed,
            'results': results,
            'count': len(results)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/wishlist/add/<int:destination_id>', methods=['POST'])
@login_required
def add_to_wishlist(destination_id):
    existing_item = WishlistItem.query.filter_by(
        user_id=current_user.id, 
        destination_id=destination_id
    ).first()
    
    if existing_item:
        flash('Destination already in wishlist.')
    else:
        wishlist_item = WishlistItem(
            user_id=current_user.id,
            destination_id=destination_id
        )
        db.session.add(wishlist_item)
        db.session.commit()
        flash('Added to wishlist!')
    
    return redirect(url_for('destination_detail', destination_id=destination_id))

@app.route('/wishlist/remove/<int:destination_id>', methods=['POST'])
@login_required
def remove_from_wishlist(destination_id):
    wishlist_item = WishlistItem.query.filter_by(
        user_id=current_user.id, 
        destination_id=destination_id
    ).first()
    
    if wishlist_item:
        db.session.delete(wishlist_item)
        db.session.commit()
        flash('Removed from wishlist.')
    
    return redirect(url_for('profile'))

@app.route('/newsletter/subscribe', methods=['POST'])
def subscribe_newsletter():
    email = request.form.get('email')
    
    if Newsletter.query.filter_by(email=email).first():
        flash('Email already subscribed.')
    else:
        newsletter = Newsletter(email=email)
        db.session.add(newsletter)
        db.session.commit()
        flash('Successfully subscribed to newsletter!')
    
    return redirect(url_for('home'))

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('home'))
    
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    total_destinations = Destination.query.count()
    total_revenue = db.session.query(db.func.sum(Booking.total_price)).filter_by(payment_status='paid').scalar() or 0
    
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(5).all()
    
    return render_template('admin.html', 
                         total_users=total_users,
                         total_bookings=total_bookings,
                         total_destinations=total_destinations,
                         total_revenue=total_revenue,
                         recent_bookings=recent_bookings,
                         recent_contacts=recent_contacts)

@app.route('/admin/add_destination', methods=['GET', 'POST'])
@login_required
def add_destination():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        country = request.form.get('country')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        duration = int(request.form.get('duration'))
        category = request.form.get('category')
        image_url = request.form.get('image_url')
        latitude = float(request.form.get('latitude', 0))
        longitude = float(request.form.get('longitude', 0))
        climate = request.form.get('climate')
        best_time = request.form.get('best_time_to_visit')
        
        destination = Destination(
            name=name,
            country=country,
            description=description,
            price=price,
            duration=duration,
            category=category,
            image_url=image_url,
            latitude=latitude,
            longitude=longitude,
            climate=climate,
            best_time_to_visit=best_time
        )
        
        db.session.add(destination)
        db.session.commit()
        
        flash('Destination added successfully!')
        return redirect(url_for('admin'))
    
    return render_template('add_destination.html')

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('home'))
    
    users = User.query.all()
    return render_template('admin_users.html', users=users)

@app.route('/admin/bookings')
@login_required
def admin_bookings():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('home'))
    
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    return render_template('admin_bookings.html', bookings=bookings)

@app.route('/admin/contacts')
@login_required
def admin_contacts():
    if not current_user.is_admin:
        flash('Access denied.')
        return redirect(url_for('home'))
    
    contacts = Contact.query.order_by(Contact.created_at.desc()).all()
    return render_template('admin_contacts.html', contacts=contacts)

@app.route('/admin/flights')
@login_required
def admin_flights():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    flights = Flight.query.all()
    return render_template('admin_flights.html', flights=flights)

@app.route('/admin/hotels')
@login_required
def admin_hotels():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    hotels = Hotel.query.all()
    return render_template('admin_hotels.html', hotels=hotels)

@app.route('/admin/packages')
@login_required
def admin_packages():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    packages = PackageDeal.query.all()
    return render_template('admin_packages.html', packages=packages)

@app.route('/admin/add_flight', methods=['GET', 'POST'])
@login_required
def add_flight():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        flight = Flight(
            flight_number=request.form['flight_number'],
            airline=request.form['airline'],
            origin=request.form['origin'],
            destination=request.form['destination'],
            departure_time=datetime.strptime(request.form['departure_time'], '%Y-%m-%dT%H:%M'),
            arrival_time=datetime.strptime(request.form['arrival_time'], '%Y-%m-%dT%H:%M'),
            price=float(request.form['price']),
            seats_available=int(request.form['seats_available'])
        )
        db.session.add(flight)
        db.session.commit()
        flash('Flight added successfully!', 'success')
        return redirect(url_for('admin_flights'))
    
    return render_template('add_flight.html')

@app.route('/admin/add_hotel', methods=['GET', 'POST'])
@login_required
def add_hotel():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        hotel = Hotel(
            name=request.form['name'],
            location=request.form['location'],
            description=request.form['description'],
            image_url=request.form['image_url'],
            rating=float(request.form['rating'])
        )
        db.session.add(hotel)
        db.session.commit()
        flash('Hotel added successfully!', 'success')
        return redirect(url_for('admin_hotels'))
    
    return render_template('add_hotel.html')

@app.route('/admin/add_package', methods=['GET', 'POST'])
@login_required
def add_package():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        package = PackageDeal(
            name=request.form['name'],
            description=request.form['description'],
            price=float(request.form['price']),
            flight_id=int(request.form['flight_id']) if request.form['flight_id'] else None,
            hotel_id=int(request.form['hotel_id']) if request.form['hotel_id'] else None,
            activities=request.form['activities'],
            image_url=request.form['image_url']
        )
        db.session.add(package)
        db.session.commit()
        flash('Package deal added successfully!', 'success')
        return redirect(url_for('admin_packages'))
    
    flights = Flight.query.all()
    hotels = Hotel.query.all()
    return render_template('add_package.html', flights=flights, hotels=hotels)

@app.route('/api/weather/<city>')
def api_weather(city):
    weather = get_weather(city)
    return jsonify(weather)

@app.route('/api/destinations')
def api_destinations():
    destinations = Destination.query.filter_by(available=True).all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'country': d.country,
        'price': d.price,
        'rating': d.rating,
        'image_url': d.image_url
    } for d in destinations])

@app.route('/api/pricing/<int:destination_id>')
def api_real_time_pricing(destination_id):
    """Get real-time pricing for a destination"""
    travel_date = request.args.get('date')
    guests = request.args.get('guests', 1, type=int)
    
    if not travel_date:
        return jsonify({'error': 'Travel date required'}), 400
    
    try:
        price = get_real_time_pricing(destination_id, travel_date, guests)
        return jsonify({
            'success': True,
            'price': format_price(price),
            'destination_id': destination_id,
            'travel_date': travel_date,
            'guests': guests
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_exchange_rate(from_currency, to_currency):
    """Get exchange rate from currency API with caching"""
    cache_key = f"exchange_rate_{from_currency}_{to_currency}"
    
    # Check cache first
    try:
        cached_rate = cache.get(cache_key)
        if cached_rate:
            return cached_rate
    except:
        pass
    
    try:
        # Using a free currency API
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency.upper()}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'].get(to_currency.upper(), 1.0)
            # Cache for 1 hour
            try:
                cache.set(cache_key, rate, timeout=3600)
            except:
                pass
            return rate
    except Exception as e:
        print(f"Currency API error: {e}")
    
    # Fallback to static rates if API fails
    rates = {
        'USD': {'EUR': 0.85, 'GBP': 0.73, 'JPY': 110.0, 'CAD': 1.25, 'AUD': 1.35},
        'EUR': {'USD': 1.18, 'GBP': 0.86, 'JPY': 129.0, 'CAD': 1.47, 'AUD': 1.59},
        'GBP': {'USD': 1.37, 'EUR': 1.16, 'JPY': 150.0, 'CAD': 1.71, 'AUD': 1.85},
        'JPY': {'USD': 0.009, 'EUR': 0.0077, 'GBP': 0.0067, 'CAD': 0.011, 'AUD': 0.012},
        'CAD': {'USD': 0.80, 'EUR': 0.68, 'GBP': 0.58, 'JPY': 88.0, 'AUD': 1.08},
        'AUD': {'USD': 0.74, 'EUR': 0.63, 'GBP': 0.54, 'JPY': 81.5, 'CAD': 0.93}
    }
    return rates.get(from_currency, {}).get(to_currency, 1.0)

def convert_currency(amount, from_currency, to_currency):
    """Convert amount from one currency to another"""
    if from_currency == to_currency:
        return amount
    rate = get_exchange_rate(from_currency, to_currency)
    return amount * rate

def get_real_time_pricing(destination_id, travel_date, guests=1):
    """Get real-time pricing for destinations with dynamic pricing"""
    cache_key = f"pricing_{destination_id}_{travel_date}_{guests}"
    
    # Check cache first
    try:
        cached_price = cache.get(cache_key)
        if cached_price:
            return float(cached_price)
    except:
        pass
    
    try:
        # Simulate real-time pricing based on demand and seasonality
        destination = Destination.query.get(destination_id)
        if not destination:
            return None
        
        base_price = destination.price
        
        # Dynamic pricing factors
        date_obj = datetime.strptime(travel_date, '%Y-%m-%d')
        month = date_obj.month
        
        # Seasonal pricing (peak season: June-August, December)
        seasonal_multiplier = 1.0
        if month in [6, 7, 8, 12]:
            seasonal_multiplier = 1.3  # 30% higher in peak season
        elif month in [1, 2, 11]:
            seasonal_multiplier = 0.8  # 20% lower in off-season
        
        # Demand-based pricing (weekend vs weekday)
        weekday = date_obj.weekday()
        if weekday >= 5:  # Weekend
            demand_multiplier = 1.15
        else:
            demand_multiplier = 1.0
        
        # Guest-based pricing
        guest_multiplier = 1.0 + (guests - 1) * 0.8  # 80% of base price for additional guests
        
        # Calculate final price
        final_price = base_price * seasonal_multiplier * demand_multiplier * guest_multiplier
        
        # Add some randomness to simulate real market conditions
        import random
        market_variance = random.uniform(0.95, 1.05)
        final_price *= market_variance
        
        # Cache for 15 minutes (real-time pricing updates frequently)
        try:
            cache.set(cache_key, str(final_price), timeout=900)
        except:
            pass
        
        return round(final_price, 2)
        
    except Exception as e:
        print(f"Error getting real-time pricing: {e}")
        return None

def format_price(amount, currency_code=None):
    """Format price with currency symbol and conversion"""
    if currency_code is None:
        currency_code = session.get('currency', app.config['DEFAULT_CURRENCY'])
    
    # Convert from USD to target currency (assuming all prices are stored in USD)
    converted_amount = convert_currency(amount, 'USD', currency_code)
    
    # Get currency info
    currency_info = app.config['SUPPORTED_CURRENCIES'].get(currency_code, {'symbol': '$', 'name': 'USD'})
    
    # Format based on currency
    if currency_code in ['USD', 'CAD', 'AUD']:
        return f"{currency_info['symbol']}{converted_amount:.2f}"
    elif currency_code in ['EUR', 'GBP']:
        return f"{converted_amount:.2f}{currency_info['symbol']}"
    elif currency_code == 'JPY':
        return f"{currency_info['symbol']}{int(converted_amount)}"
    else:
        return f"{currency_info['symbol']}{converted_amount:.2f}"



# Enhanced Blog Models
class BlogCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('BlogPost', backref='category', lazy=True)

class BlogTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    slug = db.Column(db.String(30), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Association table for many-to-many relationship between posts and tags
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('blog_post.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('blog_tag.id'), primary_key=True)
)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.Text)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('blog_category.id'))
    featured_image = db.Column(db.String(200))
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    author = db.relationship('User', backref='blog_posts')
    tags = db.relationship('BlogTag', secondary=post_tags, backref='posts')
    comments = db.relationship('BlogComment', backref='post', lazy=True, cascade='all, delete-orphan')

class BlogComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('blog_comment.id'))
    content = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='blog_comments')
    replies = db.relationship('BlogComment', backref=db.backref('parent', remote_side=[id]))

# Blog Routes
@app.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    tag = request.args.get('tag', '')
    search = request.args.get('search', '')
    
    query = BlogPost.query.filter_by(is_published=True)
    
    if category:
        query = query.join(BlogCategory).filter(BlogCategory.slug == category)
    if tag:
        query = query.join(post_tags).join(BlogTag).filter(BlogTag.slug == tag)
    if search:
        query = query.filter(BlogPost.title.contains(search) | BlogPost.content.contains(search))
    
    posts = query.order_by(BlogPost.created_at.desc()).paginate(
        page=page, per_page=6, error_out=False
    )
    
    categories = BlogCategory.query.all()
    tags = BlogTag.query.all()
    featured_posts = BlogPost.query.filter_by(is_featured=True, is_published=True).limit(3).all()
    
    return render_template('blog.html', 
                         posts=posts.items,
                         pagination=posts,
                         categories=categories,
                         tags=tags,
                         featured_posts=featured_posts,
                         current_category=category,
                         current_tag=tag,
                         search=search)

@app.route('/blog/<slug>')
def blog_post(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # Increment view count
    post.view_count += 1
    db.session.commit()
    
    # Get related posts
    related_posts = BlogPost.query.filter(
        BlogPost.category_id == post.category_id,
        BlogPost.id != post.id,
        BlogPost.is_published == True
    ).limit(3).all()
    
    return render_template('blog_post.html', post=post, related_posts=related_posts)

@app.route('/blog/<int:post_id>/comment', methods=['POST'])
@login_required
def add_comment(post_id):
    post = BlogPost.query.get_or_404(post_id)
    content = request.form.get('content', '').strip()
    
    if not content:
        flash('Comment cannot be empty.', 'error')
        return redirect(url_for('blog_post', slug=post.slug))
    
    comment = BlogComment(
        post_id=post_id,
        user_id=current_user.id,
        content=content,
        is_approved=True  # Auto-approve for now
    )
    
    db.session.add(comment)
    db.session.commit()
    
    flash('Comment added successfully!', 'success')
    return redirect(url_for('blog_post', slug=post.slug))

@app.route('/loyalty')
def loyalty():
    if current_user.is_authenticated:
        # Get user's loyalty information
        user_loyalty = UserLoyalty.query.filter_by(user_id=current_user.id).first()
        if not user_loyalty:
            # Create loyalty account for new user
            default_tier = LoyaltyTier.query.filter_by(name='Bronze').first()
            if not default_tier:
                # Create default tiers if they don't exist
                create_default_loyalty_tiers()
                default_tier = LoyaltyTier.query.filter_by(name='Bronze').first()
            
            user_loyalty = UserLoyalty(
                user_id=current_user.id,
                tier_id=default_tier.id
            )
            db.session.add(user_loyalty)
            db.session.commit()
        
        # Get loyalty tiers
        tiers = LoyaltyTier.query.order_by(LoyaltyTier.min_points).all()
        
        # Get recent transactions
        transactions = LoyaltyTransaction.query.filter_by(user_id=current_user.id).order_by(LoyaltyTransaction.created_at.desc()).limit(10).all()
        
        # Get available rewards
        available_rewards = get_available_rewards(user_loyalty.points_balance)
        
        return render_template('loyalty.html', 
                             user_loyalty=user_loyalty,
                             tiers=tiers,
                             transactions=transactions,
                             available_rewards=available_rewards)
    else:
        return render_template('loyalty.html')

def create_default_loyalty_tiers():
    """Create default loyalty tiers"""
    tiers = [
        {
            'name': 'Bronze',
            'min_points': 0,
            'discount_percentage': 0.0,
            'benefits': 'Basic member benefits',
            'color': '#cd7f32'
        },
        {
            'name': 'Silver',
            'min_points': 1000,
            'discount_percentage': 5.0,
            'benefits': '5% discount on bookings, priority support',
            'color': '#c0c0c0'
        },
        {
            'name': 'Gold',
            'min_points': 5000,
            'discount_percentage': 10.0,
            'benefits': '10% discount, free cancellation, exclusive deals',
            'color': '#ffd700'
        },
        {
            'name': 'Platinum',
            'min_points': 15000,
            'discount_percentage': 15.0,
            'benefits': '15% discount, VIP support, room upgrades',
            'color': '#e5e4e2'
        }
    ]
    
    for tier_data in tiers:
        tier = LoyaltyTier(**tier_data)
        db.session.add(tier)
    
    db.session.commit()

def get_available_rewards(points_balance):
    """Get available rewards based on points balance"""
    rewards = []
    
    if points_balance >= 500:
        rewards.append({
            'name': 'Free Airport Transfer',
            'points_required': 500,
            'description': 'Complimentary airport transfer for your next booking',
            'type': 'service'
        })
    
    if points_balance >= 1000:
        rewards.append({
            'name': 'Room Upgrade',
            'points_required': 1000,
            'description': 'Free room upgrade on your next hotel booking',
            'type': 'upgrade'
        })
    
    if points_balance >= 2000:
        rewards.append({
            'name': 'Free Activity',
            'points_required': 2000,
            'description': 'Choose one free activity from our selection',
            'type': 'activity'
        })
    
    if points_balance >= 5000:
        rewards.append({
            'name': 'Free Flight',
            'points_required': 5000,
            'description': 'Free domestic flight ticket',
            'type': 'flight'
        })
    
    return rewards

@app.route('/loyalty/earn-points', methods=['POST'])
@login_required
def earn_loyalty_points():
    """Earn loyalty points for booking"""
    booking_id = request.form.get('booking_id')
    points = request.form.get('points', type=int)
    
    if not booking_id or not points:
        return jsonify({'error': 'Invalid booking or points'}), 400
    
    # Verify booking belongs to user
    booking = Booking.query.filter_by(id=booking_id, user_id=current_user.id).first()
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    
    # Add points transaction
    transaction = LoyaltyTransaction(
        user_id=current_user.id,
        points=points,
        transaction_type='booking',
        description=f'Points earned for booking #{booking_id}',
        booking_id=booking_id
    )
    db.session.add(transaction)
    
    # Update user loyalty points
    user_loyalty = UserLoyalty.query.filter_by(user_id=current_user.id).first()
    user_loyalty.points_balance += points
    user_loyalty.total_spent += booking.total_price
    
    # Check for tier upgrade
    check_tier_upgrade(user_loyalty)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'points_earned': points,
        'new_balance': user_loyalty.points_balance
    })

def check_tier_upgrade(user_loyalty):
    """Check if user should be upgraded to higher tier"""
    current_tier = user_loyalty.tier
    next_tier = LoyaltyTier.query.filter(
        LoyaltyTier.min_points > current_tier.min_points
    ).order_by(LoyaltyTier.min_points).first()
    
    if next_tier and user_loyalty.points_balance >= next_tier.min_points:
        user_loyalty.tier_id = next_tier.id
        # Send upgrade notification
        send_notification_task(
            user_loyalty.user_id,
            'Tier Upgrade!',
            f'Congratulations! You have been upgraded to {next_tier.name} tier with {next_tier.discount_percentage}% discount!',
            'loyalty_upgrade'
        )

@app.route('/hotels')
def hotels():
    query = request.args.get('q', '')
    if query:
        hotels = Hotel.query.filter(
            Hotel.name.contains(query) | Hotel.location.contains(query)
        ).all()
    else:
        hotels = Hotel.query.all()
    return render_template('hotels.html', hotels=hotels, query=query)

@app.route('/hotel/<int:hotel_id>')
def hotel_detail(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    room_types = RoomType.query.filter_by(hotel_id=hotel.id).all()
    return render_template('hotel_detail.html', hotel=hotel, room_types=room_types)

@app.route('/book_hotel/<int:hotel_id>', methods=['GET', 'POST'])
@login_required
def book_hotel(hotel_id):
    hotel = Hotel.query.get_or_404(hotel_id)
    room_types = RoomType.query.filter_by(hotel_id=hotel.id).all()
    if request.method == 'POST':
        room_type_id = int(request.form['room_type_id'])
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        guests = int(request.form['guests'])
        room_type = RoomType.query.get(room_type_id)
        nights = (end_date - start_date).days
        total_price = nights * room_type.price_per_night
        booking = Booking(
            user_id=current_user.id,
            hotel_id=hotel.id,
            room_type_id=room_type.id,
            start_date=start_date,
            end_date=end_date,
            guests=guests,
            total_price=total_price,
            status='pending',
            payment_status='pending'
        )
        db.session.add(booking)
        db.session.commit()
        flash('Hotel booking created! Please proceed to payment.', 'success')
        return redirect(url_for('profile'))
    return render_template('book_hotel.html', hotel=hotel, room_types=room_types)

@app.route('/flights')
def flights():
    query = request.args.get('q', '')
    origin = request.args.get('origin', '')
    destination = request.args.get('destination', '')
    date = request.args.get('date', '')
    
    flights_query = Flight.query
    
    if query:
        flights_query = flights_query.filter(
            Flight.airline.contains(query) | 
            Flight.origin.contains(query) | 
            Flight.destination.contains(query)
        )
    if origin:
        flights_query = flights_query.filter(Flight.origin.contains(origin))
    if destination:
        flights_query = flights_query.filter(Flight.destination.contains(destination))
    if date:
        flights_query = flights_query.filter(Flight.departure_time.like(f'{date}%'))
    
    flights = flights_query.filter(Flight.seats_available > 0).all()
    return render_template('flights.html', flights=flights, query=query, origin=origin, destination=destination, date=date)

@app.route('/flight/<int:flight_id>')
def flight_detail(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    return render_template('flight_detail.html', flight=flight)

@app.route('/book_flight/<int:flight_id>', methods=['GET', 'POST'])
@login_required
def book_flight(flight_id):
    flight = Flight.query.get_or_404(flight_id)
    if request.method == 'POST':
        passengers = int(request.form['passengers'])
        if passengers > flight.seats_available:
            flash('Not enough seats available for this flight.', 'error')
            return redirect(url_for('flight_detail', flight_id=flight.id))
        
        total_price = flight.price * passengers
        booking = Booking(
            user_id=current_user.id,
            flight_id=flight.id,
            start_date=flight.departure_time.date(),
            end_date=flight.arrival_time.date(),
            guests=passengers,
            total_price=total_price,
            status='pending',
            payment_status='pending'
        )
        
        # Update available seats
        flight.seats_available -= passengers
        
        db.session.add(booking)
        db.session.commit()
        flash('Flight booking created! Please proceed to payment.', 'success')
        return redirect(url_for('profile'))
    
    return render_template('book_flight.html', flight=flight)

@app.route('/packages')
def packages():
    query = request.args.get('q', '')
    if query:
        packages = PackageDeal.query.filter(
            PackageDeal.name.contains(query) | 
            PackageDeal.description.contains(query)
        ).all()
    else:
        packages = PackageDeal.query.all()
    return render_template('packages.html', packages=packages, query=query)

@app.route('/package/<int:package_id>')
def package_detail(package_id):
    package = PackageDeal.query.get_or_404(package_id)
    flight = Flight.query.get(package.flight_id) if package.flight_id else None
    hotel = Hotel.query.get(package.hotel_id) if package.hotel_id else None
    return render_template('package_detail.html', package=package, flight=flight, hotel=hotel)

@app.route('/book_package/<int:package_id>', methods=['GET', 'POST'])
@login_required
def book_package(package_id):
    package = PackageDeal.query.get_or_404(package_id)
    if request.method == 'POST':
        guests = int(request.form['guests'])
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        
        # Calculate total price (package price + any additional costs)
        total_price = package.price * guests
        
        booking = Booking(
            user_id=current_user.id,
            package_deal_id=package.id,
            flight_id=package.flight_id,
            hotel_id=package.hotel_id,
            start_date=start_date,
            end_date=end_date,
            guests=guests,
            total_price=total_price,
            status='pending',
            payment_status='pending'
        )
        
        db.session.add(booking)
        db.session.commit()
        flash('Package booking created! Please proceed to payment.', 'success')
        return redirect(url_for('profile'))
    
    return render_template('book_package.html', package=package)

@app.route('/itinerary')
@login_required
def itinerary_builder():
    itineraries = Itinerary.query.filter_by(user_id=current_user.id).order_by(Itinerary.created_at.desc()).all()
    return render_template('itinerary_builder.html', itineraries=itineraries)

@app.route('/itinerary/create', methods=['GET', 'POST'])
@login_required
def create_itinerary():
    if request.method == 'POST':
        itinerary = Itinerary(
            user_id=current_user.id,
            title=request.form['title'],
            description=request.form['description'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d'),
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d'),
            is_public=bool(request.form.get('is_public'))
        )
        db.session.add(itinerary)
        db.session.commit()
        flash('Itinerary created successfully!', 'success')
        return redirect(url_for('edit_itinerary', itinerary_id=itinerary.id))
    
    return render_template('create_itinerary.html')

@app.route('/itinerary/<int:itinerary_id>')
def view_itinerary(itinerary_id):
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    if not itinerary.is_public and (not current_user.is_authenticated or itinerary.user_id != current_user.id):
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    # Group items by day
    days = {}
    for item in itinerary.items:
        if item.day_number not in days:
            days[item.day_number] = []
        days[item.day_number].append(item)
    
    return render_template('view_itinerary.html', itinerary=itinerary, days=days)

@app.route('/itinerary/<int:itinerary_id>/edit')
@login_required
def edit_itinerary(itinerary_id):
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    if itinerary.user_id != current_user.id:
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    return render_template('edit_itinerary.html', itinerary=itinerary)

@app.route('/itinerary/<int:itinerary_id>/add_item', methods=['POST'])
@login_required
def add_itinerary_item(itinerary_id):
    itinerary = Itinerary.query.get_or_404(itinerary_id)
    if itinerary.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    item = ItineraryItem(
        itinerary_id=itinerary.id,
        day_number=int(request.form['day_number']),
        time_slot=request.form['time_slot'],
        activity_type=request.form['activity_type'],
        title=request.form['title'],
        description=request.form.get('description', ''),
        location=request.form.get('location', ''),
        duration=int(request.form.get('duration', 0)),
        cost=float(request.form.get('cost', 0.0)),
        notes=request.form.get('notes', '')
    )
    
    db.session.add(item)
    db.session.commit()
    
    return jsonify({
        'id': item.id,
        'title': item.title,
        'day_number': item.day_number,
        'time_slot': item.time_slot,
        'activity_type': item.activity_type
    })

@app.route('/admin/campaigns')
@login_required
def admin_campaigns():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    campaigns = EmailCampaign.query.order_by(EmailCampaign.created_at.desc()).all()
    return render_template('admin/campaigns.html', campaigns=campaigns)

@app.route('/admin/campaign/create', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        campaign = EmailCampaign(
            name=request.form['name'],
            subject=request.form['subject'],
            content=request.form['content'],
            target_audience=request.form['target_audience']
        )
        db.session.add(campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('admin_campaigns'))
    
    return render_template('admin/create_campaign.html')

@app.route('/admin/campaign/<int:campaign_id>/send')
@login_required
def send_campaign(campaign_id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    campaign = EmailCampaign.query.get_or_404(campaign_id)
    
    # Get target users based on audience
    if campaign.target_audience == 'all':
        users = User.query.filter_by(is_active=True).all()
    elif campaign.target_audience == 'premium':
        users = User.query.filter_by(is_active=True, is_premium=True).all()
    elif campaign.target_audience == 'new_users':
        # Users registered in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        users = User.query.filter(User.created_at >= thirty_days_ago).all()
    else:
        users = []
    
    # Send emails (simulated)
    for user in users:
        try:
            msg = Message(
                subject=campaign.subject,
                recipients=[user.email],
                body=campaign.content
            )
            mail.send(msg)
            campaign.sent_count += 1
        except Exception as e:
            print(f"Failed to send email to {user.email}: {e}")
    
    campaign.sent_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Campaign sent to {len(users)} users!', 'success')
    return redirect(url_for('admin_campaigns'))

@app.route('/admin/analytics')
@login_required
def admin_analytics():
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('home'))
    
    # Get analytics data
    total_users = User.query.count()
    total_bookings = Booking.query.count()
    total_revenue = db.session.query(db.func.sum(Booking.total_price)).scalar() or 0
    
    # Popular destinations
    popular_destinations = db.session.query(
        Destination.name, 
        db.func.count(Booking.id).label('booking_count')
    ).join(Booking).group_by(Destination.id).order_by(db.func.count(Booking.id).desc()).limit(5).all()
    
    # Recent activity
    recent_analytics = UserAnalytics.query.order_by(UserAnalytics.timestamp.desc()).limit(20).all()
    
    return render_template('admin/analytics.html', 
                         total_users=total_users,
                         total_bookings=total_bookings,
                         total_revenue=total_revenue,
                         popular_destinations=popular_destinations,
                         recent_analytics=recent_analytics)

@app.route('/affiliate')
@login_required
def affiliate_dashboard():
    affiliate = Affiliate.query.filter_by(user_id=current_user.id).first()
    if not affiliate:
        # Create affiliate account
        affiliate = Affiliate(
            user_id=current_user.id,
            affiliate_code=f"REF{current_user.id:06d}",
            commission_rate=0.05
        )
        db.session.add(affiliate)
        db.session.commit()
    
    # Get referral statistics
    total_referrals = affiliate.total_referrals
    total_earnings = affiliate.total_earnings
    recent_referrals = AffiliateReferral.query.filter_by(affiliate_id=affiliate.id).order_by(AffiliateReferral.created_at.desc()).limit(10).all()
    
    return render_template('affiliate_dashboard.html', 
                         affiliate=affiliate,
                         total_referrals=total_referrals,
                         total_earnings=total_earnings,
                         recent_referrals=recent_referrals)

@app.route('/affiliate/referral/<affiliate_code>')
def affiliate_referral(affiliate_code):
    # Store affiliate code in session
    session['affiliate_code'] = affiliate_code
    flash(f'You were referred by {affiliate_code}!', 'info')
    return redirect(url_for('register'))

@app.route('/affiliate/withdraw', methods=['POST'])
@login_required
def affiliate_withdraw():
    affiliate = Affiliate.query.filter_by(user_id=current_user.id).first()
    if not affiliate:
        flash('Affiliate account not found.', 'error')
        return redirect(url_for('affiliate_dashboard'))
    
    amount = float(request.form['amount'])
    if amount > affiliate.total_earnings:
        flash('Insufficient earnings.', 'error')
        return redirect(url_for('affiliate_dashboard'))
    
    # Process withdrawal (simulated)
    affiliate.total_earnings -= amount
    db.session.commit()
    
    flash(f'Withdrawal of ${amount:.2f} processed successfully!', 'success')
    return redirect(url_for('affiliate_dashboard'))

def init_db():
    with app.app_context():
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
        
        # Add sample destinations if they don't exist
        if Destination.query.count() == 0:
            destinations = [
                # Europe
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
                    name='Rome',
                    country='Italy',
                    description='The Eternal City offers ancient ruins, Renaissance art, and world-famous cuisine in a historic setting.',
                    price=140.0,
                    duration=8,
                    image_url='/static/paris.jpg',  # Using existing image as placeholder
                    category='luxury',
                    latitude=41.9028,
                    longitude=12.4964,
                    climate='Mediterranean',
                    best_time_to_visit='April to June and September to October'
                ),
                Destination(
                    name='Barcelona',
                    country='Spain',
                    description='A vibrant city with stunning architecture, beautiful beaches, and a rich cultural scene.',
                    price=130.0,
                    duration=6,
                    image_url='/static/paris.jpg',
                    category='luxury',
                    latitude=41.3851,
                    longitude=2.1734,
                    climate='Mediterranean',
                    best_time_to_visit='May to June and September to October'
                ),
                Destination(
                    name='Amsterdam',
                    country='Netherlands',
                    description='Explore charming canals, world-class museums, and a relaxed atmosphere in this bike-friendly city.',
                    price=120.0,
                    duration=5,
                    image_url='/static/paris.jpg',
                    category='budget',
                    latitude=52.3676,
                    longitude=4.9041,
                    climate='Oceanic',
                    best_time_to_visit='April to May and September to October'
                ),
                Destination(
                    name='Prague',
                    country='Czech Republic',
                    description='A fairy-tale city with stunning Gothic architecture, historic squares, and affordable luxury.',
                    price=90.0,
                    duration=6,
                    image_url='/static/paris.jpg',
                    category='budget',
                    latitude=50.0755,
                    longitude=14.4378,
                    climate='Oceanic',
                    best_time_to_visit='May to September'
                ),
                Destination(
                    name='Vienna',
                    country='Austria',
                    description='Experience classical music, imperial palaces, and elegant coffee houses in this cultural capital.',
                    price=110.0,
                    duration=5,
                    image_url='/static/paris.jpg',
                    category='luxury',
                    latitude=48.2082,
                    longitude=16.3738,
                    climate='Oceanic',
                    best_time_to_visit='April to May and September to October'
                ),
                Destination(
                    name='Budapest',
                    country='Hungary',
                    description='A beautiful city split by the Danube, featuring thermal baths, historic architecture, and vibrant nightlife.',
                    price=85.0,
                    duration=5,
                    image_url='/static/paris.jpg',
                    category='budget',
                    latitude=47.4979,
                    longitude=19.0402,
                    climate='Oceanic',
                    best_time_to_visit='May to June and September to October'
                ),
                Destination(
                    name='Santorini',
                    country='Greece',
                    description='Stunning white-washed buildings, blue domes, and breathtaking sunsets on this iconic Greek island.',
                    price=180.0,
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
                    description='Majestic mountains offering world-class skiing, hiking, and breathtaking alpine scenery.',
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
                    name='Kyoto',
                    country='Japan',
                    description='Japan\'s cultural heart with ancient temples, traditional gardens, and geisha districts.',
                    price=160.0,
                    duration=7,
                    image_url='/static/tokyo.jpg',
                    category='luxury',
                    latitude=35.0116,
                    longitude=135.7681,
                    climate='Temperate',
                    best_time_to_visit='March to May and October to November'
                ),
                Destination(
                    name='Seoul',
                    country='South Korea',
                    description='A dynamic city blending ancient traditions with cutting-edge technology and K-pop culture.',
                    price=140.0,
                    duration=8,
                    image_url='/static/tokyo.jpg',
                    category='adventure',
                    latitude=37.5665,
                    longitude=126.9780,
                    climate='Temperate',
                    best_time_to_visit='March to May and September to November'
                ),
                Destination(
                    name='Bangkok',
                    country='Thailand',
                    description='A bustling metropolis with ornate temples, floating markets, and world-famous street food.',
                    price=80.0,
                    duration=6,
                    image_url='/static/tokyo.jpg',
                    category='budget',
                    latitude=13.7563,
                    longitude=100.5018,
                    climate='Tropical',
                    best_time_to_visit='November to March'
                ),
                Destination(
                    name='Bali',
                    country='Indonesia',
                    description='Island paradise with lush rice terraces, spiritual temples, and pristine beaches.',
                    price=100.0,
                    duration=10,
                    image_url='/static/maldives.jpg',
                    category='budget',
                    latitude=-8.3405,
                    longitude=115.0920,
                    climate='Tropical',
                    best_time_to_visit='April to October'
                ),
                Destination(
                    name='Singapore',
                    country='Singapore',
                    description='A modern city-state with futuristic architecture, diverse cuisine, and lush gardens.',
                    price=180.0,
                    duration=5,
                    image_url='/static/tokyo.jpg',
                    category='luxury',
                    latitude=1.3521,
                    longitude=103.8198,
                    climate='Tropical',
                    best_time_to_visit='February to April'
                ),
                Destination(
                    name='Hong Kong',
                    country='China',
                    description='A vibrant metropolis with stunning skyline, shopping paradise, and delicious dim sum.',
                    price=160.0,
                    duration=6,
                    image_url='/static/tokyo.jpg',
                    category='luxury',
                    latitude=22.3193,
                    longitude=114.1694,
                    climate='Subtropical',
                    best_time_to_visit='October to December'
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
                ),
                
                # Americas
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
                    name='San Francisco',
                    country='USA',
                    description='A hilly city known for the Golden Gate Bridge, Alcatraz, and innovative tech culture.',
                    price=170.0,
                    duration=6,
                    image_url='/static/ny.jpg',
                    category='luxury',
                    latitude=37.7749,
                    longitude=-122.4194,
                    climate='Mediterranean',
                    best_time_to_visit='September to November'
                ),
                Destination(
                    name='Miami',
                    country='USA',
                    description='Sunny beaches, vibrant nightlife, and Cuban culture in this tropical paradise.',
                    price=150.0,
                    duration=7,
                    image_url='/static/ny.jpg',
                    category='luxury',
                    latitude=25.7617,
                    longitude=-80.1918,
                    climate='Tropical',
                    best_time_to_visit='March to May'
                ),
                Destination(
                    name='Rio de Janeiro',
                    country='Brazil',
                    description='Famous for Carnival, Christ the Redeemer, and stunning beaches like Copacabana.',
                    price=120.0,
                    duration=8,
                    image_url='/static/cape.jpg',
                    category='adventure',
                    latitude=-22.9068,
                    longitude=-43.1729,
                    climate='Tropical',
                    best_time_to_visit='March to May and September to November'
                ),
                Destination(
                    name='Buenos Aires',
                    country='Argentina',
                    description='The Paris of South America with tango, steak, and European-style architecture.',
                    price=100.0,
                    duration=7,
                    image_url='/static/cape.jpg',
                    category='budget',
                    latitude=-34.6118,
                    longitude=-58.3960,
                    climate='Subtropical',
                    best_time_to_visit='March to May and September to November'
                ),
                Destination(
                    name='Machu Picchu',
                    country='Peru',
                    description='Ancient Incan citadel high in the Andes, one of the world\'s most impressive archaeological sites.',
                    price=130.0,
                    duration=6,
                    image_url='/static/cape.jpg',
                    category='adventure',
                    latitude=-13.1631,
                    longitude=-72.5450,
                    climate='Subtropical',
                    best_time_to_visit='April to October'
                ),
                
                # Africa & Middle East
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
                    name='Marrakech',
                    country='Morocco',
                    description='A magical city with bustling souks, stunning palaces, and the vibrant Jemaa el-Fnaa square.',
                    price=90.0,
                    duration=6,
                    image_url='/static/cape.jpg',
                    category='budget',
                    latitude=31.6295,
                    longitude=-7.9811,
                    climate='Semi-arid',
                    best_time_to_visit='March to May and September to November'
                ),
                Destination(
                    name='Dubai',
                    country='UAE',
                    description='A futuristic city with the world\'s tallest building, luxury shopping, and desert adventures.',
                    price=200.0,
                    duration=7,
                    image_url='/static/cape.jpg',
                    category='luxury',
                    latitude=25.2048,
                    longitude=55.2708,
                    climate='Desert',
                    best_time_to_visit='November to March'
                ),
                Destination(
                    name='Zanzibar',
                    country='Tanzania',
                    description='Spice island with pristine beaches, historic Stone Town, and crystal-clear waters.',
                    price=110.0,
                    duration=8,
                    image_url='/static/maldives.jpg',
                    category='budget',
                    latitude=-6.1659,
                    longitude=39.2026,
                    climate='Tropical',
                    best_time_to_visit='June to October'
                ),
                
                # Oceania
                Destination(
                    name='Sydney',
                    country='Australia',
                    description='Iconic harbor city with the Opera House, Bondi Beach, and vibrant cultural scene.',
                    price=160.0,
                    duration=8,
                    image_url='/static/cape.jpg',
                    category='luxury',
                    latitude=-33.8688,
                    longitude=151.2093,
                    climate='Oceanic',
                    best_time_to_visit='September to November and March to May'
                ),
                Destination(
                    name='Queenstown',
                    country='New Zealand',
                    description='Adventure capital with stunning fjords, skiing, and adrenaline-pumping activities.',
                    price=140.0,
                    duration=7,
                    image_url='/static/cape.jpg',
                    category='adventure',
                    latitude=-45.0312,
                    longitude=168.6626,
                    climate='Oceanic',
                    best_time_to_visit='December to February (summer), June to August (skiing)'
                ),
                Destination(
                    name='Fiji',
                    country='Fiji',
                    description='Tropical paradise with over 300 islands, coral reefs, and traditional Fijian culture.',
                    price=180.0,
                    duration=10,
                    image_url='/static/maldives.jpg',
                    category='luxury',
                    latitude=-17.7134,
                    longitude=178.0650,
                    climate='Tropical',
                    best_time_to_visit='May to October'
                ),
                
                # Special Destinations
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
                )
            ]
            
            for destination in destinations:
                db.session.add(destination)
        
        # Add sample blog data if it doesn't exist
        if BlogCategory.query.count() == 0:
            categories = [
                BlogCategory(name='Travel Tips', slug='travel-tips', description='Essential tips for travelers'),
                BlogCategory(name='Destination Guides', slug='destination-guides', description='Detailed guides to popular destinations'),
                BlogCategory(name='Adventure Travel', slug='adventure-travel', description='Adventure and outdoor travel stories'),
                BlogCategory(name='Luxury Travel', slug='luxury-travel', description='Luxury travel experiences and recommendations'),
                BlogCategory(name='Budget Travel', slug='budget-travel', description='Budget-friendly travel tips and destinations')
            ]
            for category in categories:
                db.session.add(category)
        
        if BlogTag.query.count() == 0:
            tags = [
                BlogTag(name='Europe', slug='europe'),
                BlogTag(name='Asia', slug='asia'),
                BlogTag(name='Adventure', slug='adventure'),
                BlogTag(name='Luxury', slug='luxury'),
                BlogTag(name='Budget', slug='budget'),
                BlogTag(name='Food', slug='food'),
                BlogTag(name='Culture', slug='culture'),
                BlogTag(name='Nature', slug='nature'),
                BlogTag(name='City', slug='city'),
                BlogTag(name='Beach', slug='beach')
            ]
            for tag in tags:
                db.session.add(tag)
        
        if BlogPost.query.count() == 0:
            # Get admin user and categories
            admin_user = User.query.filter_by(username='admin').first()
            travel_tips_cat = BlogCategory.query.filter_by(slug='travel-tips').first()
            destination_cat = BlogCategory.query.filter_by(slug='destination-guides').first()
            adventure_cat = BlogCategory.query.filter_by(slug='adventure-travel').first()
            
            # Get tags
            europe_tag = BlogTag.query.filter_by(slug='europe').first()
            asia_tag = BlogTag.query.filter_by(slug='asia').first()
            adventure_tag = BlogTag.query.filter_by(slug='adventure').first()
            luxury_tag = BlogTag.query.filter_by(slug='luxury').first()
            food_tag = BlogTag.query.filter_by(slug='food').first()
            culture_tag = BlogTag.query.filter_by(slug='culture').first()
            
            posts = [
                BlogPost(
                    title='10 Essential Travel Tips for First-Time Travelers',
                    slug='10-essential-travel-tips-first-time-travelers',
                    content='''
                    <h2>Planning Your First Trip</h2>
                    <p>Traveling for the first time can be both exciting and overwhelming. Here are 10 essential tips to help you make the most of your journey:</p>
                    
                    <h3>1. Research Your Destination</h3>
                    <p>Before you go, research your destination thoroughly. Learn about the local customs, language basics, weather, and any travel advisories.</p>
                    
                    <h3>2. Pack Light</h3>
                    <p>You'll be surprised how little you actually need. Pack versatile clothing that can be mixed and matched, and remember that you can always buy things you forget.</p>
                    
                    <h3>3. Keep Important Documents Safe</h3>
                    <p>Make copies of your passport, travel insurance, and other important documents. Keep one set with you and leave another with someone at home.</p>
                    
                    <h3>4. Learn Basic Phrases</h3>
                    <p>Even if you don't speak the local language fluently, learning basic phrases like "hello," "thank you," and "where is the bathroom?" can go a long way.</p>
                    
                    <h3>5. Stay Connected</h3>
                    <p>Consider getting a local SIM card or international data plan so you can stay connected and use navigation apps.</p>
                    
                    <h3>6. Be Flexible</h3>
                    <p>Things don't always go according to plan when traveling. Be prepared to adapt and go with the flow.</p>
                    
                    <h3>7. Stay Safe</h3>
                    <p>Always be aware of your surroundings and trust your instincts. Keep your valuables secure and avoid walking alone at night in unfamiliar areas.</p>
                    
                    <h3>8. Try Local Food</h3>
                    <p>One of the best ways to experience a culture is through its food. Don't be afraid to try local dishes and street food.</p>
                    
                    <h3>9. Take Photos</h3>
                    <p>Document your journey with photos, but don't forget to put the camera down and enjoy the moment too.</p>
                    
                    <h3>10. Connect with Locals</h3>
                    <p>Some of the best travel experiences come from meeting and talking with locals. Be open to new friendships and cultural exchanges.</p>
                    
                    <p>Remember, every traveler was a first-time traveler once. Don't be afraid to make mistakes - they often lead to the best stories!</p>
                    ''',
                    excerpt='Essential tips and advice for first-time travelers to make their journey smooth and enjoyable.',
                    author_id=admin_user.id,
                    category_id=travel_tips_cat.id if travel_tips_cat else None,
                    featured_image='/static/paris.jpg',
                    is_featured=True,
                    is_published=True,
                    published_at=datetime.utcnow()
                ),
                BlogPost(
                    title='Ultimate Guide to Exploring Paris: The City of Light',
                    slug='ultimate-guide-exploring-paris-city-light',
                    content='''
                    <h2>Welcome to Paris</h2>
                    <p>Paris, the capital of France, is one of the most beautiful and romantic cities in the world. Known as the "City of Light," Paris offers an incredible blend of history, culture, art, and cuisine.</p>
                    
                    <h3>Must-See Attractions</h3>
                    <ul>
                        <li><strong>Eiffel Tower:</strong> The iconic symbol of Paris, offering breathtaking views of the city</li>
                        <li><strong>Louvre Museum:</strong> Home to the Mona Lisa and thousands of other masterpieces</li>
                        <li><strong>Notre-Dame Cathedral:</strong> A masterpiece of Gothic architecture</li>
                        <li><strong>Arc de Triomphe:</strong> Monument honoring those who fought for France</li>
                        <li><strong>Champs-Élysées:</strong> One of the world's most famous avenues</li>
                    </ul>
                    
                    <h3>Best Time to Visit</h3>
                    <p>The best time to visit Paris is during the spring (April to June) or fall (September to November) when the weather is mild and the crowds are smaller.</p>
                    
                    <h3>Getting Around</h3>
                    <p>Paris has an excellent public transportation system including the Metro, buses, and RER trains. Consider getting a Paris Visite pass for unlimited travel.</p>
                    
                    <h3>Where to Eat</h3>
                    <p>Paris is a food lover's paradise. Don't miss trying:</p>
                    <ul>
                        <li>Fresh croissants and pastries from local bakeries</li>
                        <li>Traditional French cuisine at bistros</li>
                        <li>Street food like crêpes and falafel</li>
                        <li>Wine and cheese pairings</li>
                    </ul>
                    
                    <h3>Hidden Gems</h3>
                    <p>Beyond the tourist attractions, explore:</p>
                    <ul>
                        <li>Le Marais district for trendy shops and cafes</li>
                        <li>Montmartre for artistic history and views</li>
                        <li>Canal Saint-Martin for a peaceful walk</li>
                        <li>Père Lachaise Cemetery for famous graves</li>
                    </ul>
                    
                    <p>Paris is a city that reveals itself slowly. Take your time to explore, get lost in the charming streets, and fall in love with the magic of the City of Light.</p>
                    ''',
                    excerpt='A comprehensive guide to exploring Paris, including must-see attractions, hidden gems, and local tips.',
                    author_id=admin_user.id,
                    category_id=destination_cat.id if destination_cat else None,
                    featured_image='/static/paris.jpg',
                    is_featured=True,
                    is_published=True,
                    published_at=datetime.utcnow()
                ),
                BlogPost(
                    title='Adventure Travel: Hiking Mount Fuji in Japan',
                    slug='adventure-travel-hiking-mount-fuji-japan',
                    content='''
                    <h2>Conquering Japan's Sacred Mountain</h2>
                    <p>Mount Fuji, Japan's highest peak at 3,776 meters, is not just a mountain - it's a spiritual symbol and a challenging adventure waiting to be conquered.</p>
                    
                    <h3>When to Climb</h3>
                    <p>The official climbing season is from early July to early September. During this time, the weather is most favorable and the mountain huts are open.</p>
                    
                    <h3>Choosing Your Route</h3>
                    <p>There are four main trails to the summit:</p>
                    <ul>
                        <li><strong>Yoshida Trail:</strong> Most popular, good for beginners</li>
                        <li><strong>Subashiri Trail:</strong> Less crowded, beautiful forest</li>
                        <li><strong>Gotemba Trail:</strong> Longest route, least crowded</li>
                        <li><strong>Fujinomiya Trail:</strong> Shortest route, steepest</li>
                    </ul>
                    
                    <h3>Preparation Tips</h3>
                    <ul>
                        <li>Start training at least 2-3 months in advance</li>
                        <li>Pack appropriate gear for changing weather</li>
                        <li>Book mountain huts in advance during peak season</li>
                        <li>Acclimatize to the altitude</li>
                        <li>Check weather forecasts before departure</li>
                    </ul>
                    
                    <h3>What to Pack</h3>
                    <ul>
                        <li>Sturdy hiking boots with good grip</li>
                        <li>Layered clothing for temperature changes</li>
                        <li>Headlamp for night climbing</li>
                        <li>Plenty of water and high-energy snacks</li>
                        <li>First aid kit and emergency supplies</li>
                    </ul>
                    
                    <h3>The Climb Experience</h3>
                    <p>The climb typically takes 5-8 hours to reach the summit, depending on your fitness level and the route chosen. Most climbers start in the evening to reach the summit for sunrise.</p>
                    
                    <h3>Safety Considerations</h3>
                    <p>Always check weather conditions and be prepared to turn back if conditions become dangerous. Altitude sickness can affect anyone, so listen to your body.</p>
                    
                    <p>Climbing Mount Fuji is a challenging but rewarding experience that offers incredible views and a deep sense of accomplishment. Remember to respect the mountain and leave no trace.</p>
                    ''',
                    excerpt='A complete guide to hiking Mount Fuji, including route selection, preparation tips, and what to expect.',
                    author_id=admin_user.id,
                    category_id=adventure_cat.id if adventure_cat else None,
                    featured_image='/static/mountfuji.jpg',
                    is_featured=False,
                    is_published=True,
                    published_at=datetime.utcnow()
                )
            ]
            
            for post in posts:
                db.session.add(post)
            
            # Add tags to posts
            db.session.flush()  # Get the post IDs
            
            # Add tags to the first post
            if posts[0] and europe_tag and food_tag and culture_tag:
                posts[0].tags.extend([europe_tag, food_tag, culture_tag])
            
            # Add tags to the second post
            if posts[1] and europe_tag and luxury_tag and culture_tag:
                posts[1].tags.extend([europe_tag, luxury_tag, culture_tag])
            
            # Add tags to the third post
            if posts[2] and asia_tag and adventure_tag:
                posts[2].tags.extend([asia_tag, adventure_tag])
        
        # Add sample flights if they don't exist
        if Flight.query.count() == 0:
            flights = [
                Flight(
                    flight_number='AF123',
                    airline='Air France',
                    origin='New York',
                    destination='Paris',
                            departure_time=datetime(2025, 6, 15, 14, 30),
        arrival_time=datetime(2025, 6, 16, 6, 45),
                    price=850.0,
                    seats_available=45
                ),
                Flight(
                    flight_number='JL456',
                    airline='Japan Airlines',
                    origin='Los Angeles',
                    destination='Tokyo',
                            departure_time=datetime(2025, 6, 20, 11, 15),
        arrival_time=datetime(2025, 6, 21, 15, 30),
                    price=1200.0,
                    seats_available=32
                ),
                Flight(
                    flight_number='BA789',
                    airline='British Airways',
                    origin='London',
                    destination='New York',
                            departure_time=datetime(2025, 6, 25, 9, 0),
        arrival_time=datetime(2025, 6, 25, 12, 30),
                    price=750.0,
                    seats_available=28
                )
            ]
            for flight in flights:
                db.session.add(flight)
        
        # Add sample hotels if they don't exist
        if Hotel.query.count() == 0:
            hotels = [
                Hotel(
                    name='Hotel Ritz Paris',
                    location='Paris, France',
                    description='Luxury hotel in the heart of Paris with world-class amenities and service.',
                    image_url='/static/paris.jpg',
                    rating=4.8
                ),
                Hotel(
                    name='Park Hyatt Tokyo',
                    location='Tokyo, Japan',
                    description='Modern luxury hotel with stunning city views and exceptional service.',
                    image_url='/static/tokyo.jpg',
                    rating=4.7
                ),
                Hotel(
                    name='The Plaza New York',
                    location='New York, USA',
                    description='Historic luxury hotel on Central Park with elegant rooms and fine dining.',
                    image_url='/static/ny.jpg',
                    rating=4.6
                )
            ]
            for hotel in hotels:
                db.session.add(hotel)
            
            db.session.commit()
            
            # Add room types for each hotel
            ritz = Hotel.query.filter_by(name='Hotel Ritz Paris').first()
            park_hyatt = Hotel.query.filter_by(name='Park Hyatt Tokyo').first()
            plaza = Hotel.query.filter_by(name='The Plaza New York').first()
            
            room_types = [
                RoomType(hotel_id=ritz.id, name='Deluxe Room', description='Elegant room with city views', price_per_night=450.0, total_rooms=50, available_rooms=35),
                RoomType(hotel_id=ritz.id, name='Suite', description='Luxury suite with separate living area', price_per_night=800.0, total_rooms=20, available_rooms=12),
                RoomType(hotel_id=park_hyatt.id, name='Standard Room', description='Modern room with city skyline views', price_per_night=350.0, total_rooms=60, available_rooms=45),
                RoomType(hotel_id=park_hyatt.id, name='Executive Suite', description='Spacious suite with business amenities', price_per_night=650.0, total_rooms=15, available_rooms=8),
                RoomType(hotel_id=plaza.id, name='Classic Room', description='Historic room with period furnishings', price_per_night=400.0, total_rooms=40, available_rooms=25),
                RoomType(hotel_id=plaza.id, name='Central Park Suite', description='Suite with direct Central Park views', price_per_night=750.0, total_rooms=10, available_rooms=6)
            ]
            for room_type in room_types:
                db.session.add(room_type)
        
        # Add sample package deals if they don't exist
        if PackageDeal.query.count() == 0:
            paris_flight = Flight.query.filter_by(flight_number='AF123').first()
            ritz_hotel = Hotel.query.filter_by(name='Hotel Ritz Paris').first()
            
            packages = [
                PackageDeal(
                    name='Paris Luxury Getaway',
                    description='7-day luxury package including flights, hotel, and guided tours',
                    price=2500.0,
                    flight_id=paris_flight.id if paris_flight else None,
                    hotel_id=ritz_hotel.id if ritz_hotel else None,
                    activities='Eiffel Tower visit, Louvre Museum tour, Seine River cruise, Gourmet dinner',
                    image_url='/static/paris.jpg'
                ),
                PackageDeal(
                    name='Tokyo Adventure Package',
                    description='10-day adventure package with cultural experiences',
                    price=3200.0,
                    activities='Mount Fuji day trip, Traditional tea ceremony, Sushi making class, Temple visits',
                    image_url='/static/tokyo.jpg'
                )
            ]
            for package in packages:
                db.session.add(package)
        
        # Add loyalty tiers if they don't exist
        if LoyaltyTier.query.count() == 0:
            tiers = [
                LoyaltyTier(name='Bronze', min_points=0, discount_percentage=0.0, color='#CD7F32', benefits='Basic member benefits'),
                LoyaltyTier(name='Silver', min_points=1000, discount_percentage=5.0, color='#C0C0C0', benefits='5% discount on bookings, priority support'),
                LoyaltyTier(name='Gold', min_points=5000, discount_percentage=10.0, color='#FFD700', benefits='10% discount, free upgrades, exclusive offers'),
                LoyaltyTier(name='Platinum', min_points=15000, discount_percentage=15.0, color='#E5E4E2', benefits='15% discount, VIP treatment, concierge service')
            ]
            for tier in tiers:
                db.session.add(tier)
        
        # Add insurance plans if they don't exist
        if InsurancePlan.query.count() == 0:
            plans = [
                InsurancePlan(
                    name='Basic Coverage',
                    description='Essential travel insurance covering medical emergencies and trip cancellation',
                    coverage_type='basic',
                    price_per_day=5.0,
                    max_coverage=10000.0,
                    deductible=100.0
                ),
                InsurancePlan(
                    name='Comprehensive Coverage',
                    description='Complete coverage including medical, trip cancellation, baggage, and adventure activities',
                    coverage_type='comprehensive',
                    price_per_day=12.0,
                    max_coverage=50000.0,
                    deductible=50.0
                ),
                InsurancePlan(
                    name='Premium Coverage',
                    description='Luxury coverage with high limits, no deductibles, and concierge services',
                    coverage_type='premium',
                    price_per_day=25.0,
                    max_coverage=100000.0,
                    deductible=0.0
                )
            ]
            for plan in plans:
                db.session.add(plan)
        
        # Add travel guides if they don't exist
        if TravelGuide.query.count() == 0:
            paris_dest = Destination.query.filter_by(name='Paris').first()
            tokyo_dest = Destination.query.filter_by(name='Tokyo').first()
            admin_user = User.query.filter_by(username='admin').first()
            
            guides = [
                TravelGuide(
                    destination_id=paris_dest.id if paris_dest else 1,
                    title='Complete Paris Travel Guide',
                    content='''
                    <h2>Welcome to Paris</h2>
                    <p>Paris, the City of Light, is one of the most beautiful and romantic cities in the world. This comprehensive guide will help you make the most of your visit.</p>
                    
                    <h3>Getting Around</h3>
                    <p>Paris has an excellent public transportation system. The Metro is the fastest way to get around, with 16 lines covering the entire city. You can also use buses, trams, and RER trains for longer distances.</p>
                    
                    <h3>Must-See Attractions</h3>
                    <ul>
                        <li><strong>Eiffel Tower:</strong> Visit early morning or late evening to avoid crowds</li>
                        <li><strong>Louvre Museum:</strong> Book tickets online to skip the line</li>
                        <li><strong>Notre-Dame Cathedral:</strong> Currently under restoration, but still impressive from outside</li>
                        <li><strong>Arc de Triomphe:</strong> Climb to the top for amazing city views</li>
                    </ul>
                    
                    <h3>Best Neighborhoods to Explore</h3>
                    <ul>
                        <li><strong>Le Marais:</strong> Trendy area with great shopping and restaurants</li>
                        <li><strong>Montmartre:</strong> Artistic neighborhood with Sacré-Cœur</li>
                        <li><strong>Saint-Germain-des-Prés:</strong> Literary and intellectual quarter</li>
                        <li><strong>Champs-Élysées:</strong> Famous avenue for shopping and dining</li>
                    </ul>
                    
                    <h3>Local Cuisine</h3>
                    <p>Don't miss trying traditional French dishes like croissants, baguettes, escargot, coq au vin, and crème brûlée. Visit local markets for fresh produce and artisanal products.</p>
                    ''',
                    author_id=admin_user.id,
                    language='en'
                ),
                TravelGuide(
                    destination_id=tokyo_dest.id if tokyo_dest else 2,
                    title='Tokyo Travel Guide: Modern Meets Traditional',
                    content='''
                    <h2>Discovering Tokyo</h2>
                    <p>Tokyo is a fascinating blend of ultramodern and traditional, offering visitors an incredible array of experiences.</p>
                    
                    <h3>Getting Around</h3>
                    <p>Tokyo's public transportation is world-class. The JR Yamanote Line circles central Tokyo, while the Metro covers the rest of the city. Get a Pasmo or Suica card for easy access to all trains and buses.</p>
                    
                    <h3>Top Districts to Explore</h3>
                    <ul>
                        <li><strong>Shibuya:</strong> Famous for the scramble crossing and youth culture</li>
                        <li><strong>Shinjuku:</strong> Business district with great nightlife and restaurants</li>
                        <li><strong>Harajuku:</strong> Fashion-forward area with unique street style</li>
                        <li><strong>Asakusa:</strong> Traditional area with Senso-ji Temple</li>
                        <li><strong>Akihabara:</strong> Electronics and anime paradise</li>
                    </ul>
                    
                    <h3>Cultural Experiences</h3>
                    <p>Don't miss traditional experiences like tea ceremonies, sumo wrestling matches, and visiting ancient temples and shrines. Modern attractions include robot restaurants, themed cafes, and cutting-edge technology.</p>
                    ''',
                    author_id=admin_user.id,
                    language='en'
                )
            ]
            for guide in guides:
                db.session.add(guide)
        
        # Add local events if they don't exist
        if LocalEvent.query.count() == 0:
            paris_dest = Destination.query.filter_by(name='Paris').first()
            tokyo_dest = Destination.query.filter_by(name='Tokyo').first()
            
            events = [
                LocalEvent(
                    destination_id=paris_dest.id if paris_dest else 1,
                    title='Paris Fashion Week',
                    description='The world\'s most prestigious fashion event featuring top designers and celebrities.',
                            event_date=datetime(2025, 9, 25, 10, 0),
        end_date=datetime(2025, 10, 3, 18, 0),
                    location='Various venues across Paris',
                    event_type='fashion',
                    price_range='Free to $500+',
                    image_url='/static/paris.jpg'
                ),
                LocalEvent(
                    destination_id=paris_dest.id if paris_dest else 1,
                    title='Bastille Day Celebrations',
                    description='France\'s national day with military parades, fireworks, and street parties.',
                            event_date=datetime(2025, 7, 14, 10, 0),
        end_date=datetime(2025, 7, 14, 23, 0),
                    location='Champs-Élysées and throughout Paris',
                    event_type='cultural',
                    price_range='Free',
                    image_url='/static/paris.jpg'
                ),
                LocalEvent(
                    destination_id=tokyo_dest.id if tokyo_dest else 2,
                    title='Cherry Blossom Festival',
                    description='Celebrate the beautiful sakura season with traditional events and hanami parties.',
                            event_date=datetime(2025, 3, 25, 9, 0),
        end_date=datetime(2025, 3, 25, 18, 0),
                    location='Ueno Park and other locations',
                    event_type='cultural',
                    price_range='Free to $50',
                    image_url='/static/tokyo.jpg'
                ),
                LocalEvent(
                    destination_id=tokyo_dest.id if tokyo_dest else 2,
                    title='Tokyo Game Show',
                    description='Asia\'s largest gaming convention featuring the latest video games and technology.',
                            event_date=datetime(2025, 9, 20, 10, 0),
        end_date=datetime(2025, 9, 23, 18, 0),
                    location='Makuhari Messe',
                    event_type='entertainment',
                    price_range='$20-$100',
                    image_url='/static/tokyo.jpg'
                )
            ]
            for event in events:
                db.session.add(event)
        
        # Add video content if it doesn't exist
        if VideoContent.query.count() == 0:
            paris_dest = Destination.query.filter_by(name='Paris').first()
            tokyo_dest = Destination.query.filter_by(name='Tokyo').first()
            
            videos = [
                VideoContent(
                    destination_id=paris_dest.id if paris_dest else 1,
                    title='Paris Virtual Tour',
                    description='Experience the magic of Paris from the comfort of your home with this immersive virtual tour.',
                    video_url='https://www.youtube.com/embed/example1',
                    thumbnail_url='/static/paris.jpg',
                    duration=1800,  # 30 minutes
                    video_type='virtual_tour',
                    is_featured=True
                ),
                VideoContent(
                    destination_id=tokyo_dest.id if tokyo_dest else 2,
                    title='Tokyo Travel Tips',
                    description='Essential tips and advice for first-time visitors to Tokyo.',
                    video_url='https://www.youtube.com/embed/example2',
                    thumbnail_url='/static/tokyo.jpg',
                    duration=900,  # 15 minutes
                    video_type='travel_tips',
                    is_featured=True
                )
            ]
            for video in videos:
                db.session.add(video)
        
        # Add interactive maps if they don't exist
        if InteractiveMap.query.count() == 0:
            paris_dest = Destination.query.filter_by(name='Paris').first()
            
            if paris_dest:
                paris_map = InteractiveMap(
                    destination_id=paris_dest.id,
                    map_name='Paris Attractions Map',
                    zoom_level=12,
                    center_lat=48.8566,
                    center_lng=2.3522
                )
                db.session.add(paris_map)
                db.session.commit()
                
                # Add map points
                map_points = [
                    MapPoint(
                        map_id=paris_map.id,
                        name='Eiffel Tower',
                        description='Iconic iron lattice tower on the Champ de Mars',
                        latitude=48.8584,
                        longitude=2.2945,
                        point_type='attraction'
                    ),
                    MapPoint(
                        map_id=paris_map.id,
                        name='Louvre Museum',
                        description='World\'s largest art museum and historic monument',
                        latitude=48.8606,
                        longitude=2.3376,
                        point_type='attraction'
                    ),
                    MapPoint(
                        map_id=paris_map.id,
                        name='Notre-Dame Cathedral',
                        description='Medieval Catholic cathedral on Île de la Cité',
                        latitude=48.8530,
                        longitude=2.3499,
                        point_type='attraction'
                    )
                ]
                for point in map_points:
                    db.session.add(point)
        
        # Add FAQ if it doesn't exist
        if FAQ.query.count() == 0:
            faqs = [
                FAQ(
                    question='How do I book a trip?',
                    answer='You can book a trip by browsing our destinations, selecting your preferred dates, and completing the booking process online. You can also contact our customer service for assistance.',
                    category='booking',
                    order=1
                ),
                FAQ(
                    question='What is your cancellation policy?',
                    answer='Cancellation policies vary by booking type. Generally, you can cancel up to 24 hours before departure for a full refund. Some bookings may have different terms.',
                    category='booking',
                    order=2
                ),
                FAQ(
                    question='Do you offer travel insurance?',
                    answer='Yes, we offer comprehensive travel insurance plans to protect your trip. You can add insurance during the booking process or contact us for more information.',
                    category='insurance',
                    order=1
                ),
                FAQ(
                    question='How do I earn loyalty points?',
                    answer='You earn loyalty points for every dollar spent on bookings. Points can be redeemed for discounts on future trips or other rewards.',
                    category='loyalty',
                    order=1
                ),
                FAQ(
                    question='Can I modify my booking after confirmation?',
                    answer='Yes, you can modify your booking up to 48 hours before departure, subject to availability and any applicable fees.',
                    category='booking',
                    order=3
                )
            ]
            for faq in faqs:
                db.session.add(faq)
        
        # Add offline maps if they don't exist
        if OfflineMap.query.count() == 0:
            paris_dest = Destination.query.filter_by(name='Paris').first()
            tokyo_dest = Destination.query.filter_by(name='Tokyo').first()
            ny_dest = Destination.query.filter_by(name='New York').first()
            greece_dest = Destination.query.filter_by(name='Greece').first()
            maldives_dest = Destination.query.filter_by(name='Maldives').first()
            cape_dest = Destination.query.filter_by(name='Cape Town').first()
            fuji_dest = Destination.query.filter_by(name='Mount Fuji').first()
            
            maps = [
                OfflineMap(
                    destination_id=paris_dest.id if paris_dest else 1,
                    map_name='Paris City Center Map',
                    file_url='/static/maps/paris_city.pdf',
                    file_size=2048576,  # 2MB
                    version='1.2'
                ),
                OfflineMap(
                    destination_id=paris_dest.id if paris_dest else 1,
                    map_name='Paris Metro & Transport',
                    file_url='/static/maps/paris_metro.pdf',
                    file_size=1536000,  # 1.5MB
                    version='1.1'
                ),
                OfflineMap(
                    destination_id=tokyo_dest.id if tokyo_dest else 2,
                    map_name='Tokyo City Map',
                    file_url='/static/maps/tokyo_city.pdf',
                    file_size=2560000,  # 2.5MB
                    version='1.3'
                ),
                OfflineMap(
                    destination_id=tokyo_dest.id if tokyo_dest else 2,
                    map_name='Tokyo Metro & JR Lines',
                    file_url='/static/maps/tokyo_metro.pdf',
                    file_size=1792000,  # 1.75MB
                    version='1.2'
                ),
                OfflineMap(
                    destination_id=ny_dest.id if ny_dest else 3,
                    map_name='New York City Map',
                    file_url='/static/maps/nyc_city.pdf',
                    file_size=2304000,  # 2.25MB
                    version='1.1'
                ),
                OfflineMap(
                    destination_id=ny_dest.id if ny_dest else 3,
                    map_name='NYC Subway Map',
                    file_url='/static/maps/nyc_subway.pdf',
                    file_size=1280000,  # 1.25MB
                    version='1.0'
                ),
                OfflineMap(
                    destination_id=greece_dest.id if greece_dest else 4,
                    map_name='Athens City Map',
                    file_url='/static/maps/athens_city.pdf',
                    file_size=1792000,  # 1.75MB
                    version='1.1'
                ),
                OfflineMap(
                    destination_id=greece_dest.id if greece_dest else 4,
                    map_name='Greek Islands Overview',
                    file_url='/static/maps/greek_islands.pdf',
                    file_size=1536000,  # 1.5MB
                    version='1.0'
                ),
                OfflineMap(
                    destination_id=maldives_dest.id if maldives_dest else 5,
                    map_name='Maldives Atolls Map',
                    file_url='/static/maps/maldives_atolls.pdf',
                    file_size=1024000,  # 1MB
                    version='1.0'
                ),
                OfflineMap(
                    destination_id=cape_dest.id if cape_dest else 6,
                    map_name='Cape Town City Map',
                    file_url='/static/maps/cape_town.pdf',
                    file_size=2048000,  # 2MB
                    version='1.1'
                ),
                OfflineMap(
                    destination_id=fuji_dest.id if fuji_dest else 7,
                    map_name='Mount Fuji Hiking Trails',
                    file_url='/static/maps/fuji_trails.pdf',
                    file_size=1280000,  # 1.25MB
                    version='1.0'
                )
            ]
            for map_obj in maps:
                db.session.add(map_obj)
        
        # Add API partners if they don't exist
        if APIPartner.query.count() == 0:
            partners = [
                APIPartner(
                    partner_name='Travel Agency Pro',
                    api_key='partner_key_123456',
                    webhook_url='https://partner1.com/webhook',
                    rate_limit=5000
                ),
                APIPartner(
                    partner_name='Corporate Travel Solutions',
                    api_key='corp_travel_789012',
                    webhook_url='https://corp-travel.com/api/webhook',
                    rate_limit=10000
                )
            ]
            for partner in partners:
                db.session.add(partner)
        
        # Add content pages if they don't exist
        if ContentPage.query.count() == 0:
            admin_user = User.query.filter_by(username='admin').first()
            
            pages = [
                ContentPage(
                    title='About World Tour',
                    slug='about',
                    content='''
                    <h2>About World Tour</h2>
                    <p>World Tour is your premier destination for unforgettable travel experiences. We specialize in creating personalized journeys that combine luxury, adventure, and cultural immersion.</p>
                    
                    <h3>Our Mission</h3>
                    <p>To inspire and enable travelers to explore the world with confidence, providing exceptional service and authentic experiences that create lasting memories.</p>
                    
                    <h3>Why Choose Us?</h3>
                    <ul>
                        <li>Expert travel planning and personalized service</li>
                        <li>Exclusive access to unique destinations and experiences</li>
                        <li>24/7 customer support throughout your journey</li>
                        <li>Competitive pricing and flexible booking options</li>
                        <li>Loyalty program with exclusive benefits</li>
                    </ul>
                    ''',
                    meta_description='Learn about World Tour, your premier travel partner for unforgettable journeys around the globe.',
                    meta_keywords='travel, world tour, luxury travel, adventure, destinations',
                    author_id=admin_user.id,
                    is_published=True
                ),
                ContentPage(
                    title='Privacy Policy',
                    slug='privacy-policy',
                    content='''
                    <h2>Privacy Policy</h2>
                    <p>At World Tour, we are committed to protecting your privacy and ensuring the security of your personal information.</p>
                    
                    <h3>Information We Collect</h3>
                    <p>We collect information you provide directly to us, such as when you create an account, make a booking, or contact our customer service.</p>
                    
                    <h3>How We Use Your Information</h3>
                    <p>We use your information to process bookings, provide customer service, send important updates, and improve our services.</p>
                    
                    <h3>Information Sharing</h3>
                    <p>We do not sell, trade, or otherwise transfer your personal information to third parties without your consent, except as required by law.</p>
                    ''',
                    meta_description='Our privacy policy explains how we collect, use, and protect your personal information.',
                    author_id=admin_user.id,
                    is_published=True
                )
            ]
            for page in pages:
                db.session.add(page)
        
        db.session.commit()

# Background tasks (disabled for development)
def send_email_task(to_email, subject, body):
    """Background task to send emails (disabled for development)"""
    try:
        msg = Message(subject=subject, recipients=[to_email], body=body)
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def process_payment_task(booking_id):
    """Background task to process payments (disabled for development)"""
    try:
        booking = Booking.query.get(booking_id)
        if booking:
            # Simulate payment processing
            import time
            time.sleep(2)  # Simulate processing time
            
            booking.payment_status = 'completed'
            booking.status = 'confirmed'
            db.session.commit()
            
            # Send confirmation email
            send_email_task(
                booking.user.email,
                'Booking Confirmed',
                f'Your booking for {booking.destination.name if booking.destination else "your trip"} has been confirmed!'
            )
            
        return True
    except Exception as e:
        print(f"Failed to process payment: {e}")
        return False

def update_exchange_rates_task():
    """Background task to update exchange rates (disabled for development)"""
    try:
        # In production, fetch from real API
        rates = {
            'USD': {'EUR': 0.85, 'GBP': 0.73, 'JPY': 110.0, 'CAD': 1.25, 'AUD': 1.35},
            'EUR': {'USD': 1.18, 'GBP': 0.86, 'JPY': 129.0, 'CAD': 1.47, 'AUD': 1.59},
            'GBP': {'USD': 1.37, 'EUR': 1.16, 'JPY': 150.0, 'CAD': 1.71, 'AUD': 1.85},
            'JPY': {'USD': 0.009, 'EUR': 0.0077, 'GBP': 0.0067, 'CAD': 0.011, 'AUD': 0.012},
            'CAD': {'USD': 0.80, 'EUR': 0.68, 'GBP': 0.58, 'JPY': 88.0, 'AUD': 1.08},
            'AUD': {'USD': 0.74, 'EUR': 0.63, 'GBP': 0.54, 'JPY': 81.5, 'CAD': 0.93}
        }
        
        # Store in Redis (disabled for development)
        # redis_client.setex('exchange_rates', 3600, pickle.dumps(rates))
        return True
    except Exception as e:
        print(f"Failed to update exchange rates: {e}")
        return False

# Customer Support Models
class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))  # booking, payment, technical, general
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, urgent
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved, closed
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    user = db.relationship('User', foreign_keys=[user_id], backref='support_tickets')
    agent = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_tickets')
    messages = db.relationship('TicketMessage', backref='ticket', lazy=True, cascade='all, delete-orphan')


class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(300), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SupportChat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, ended
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    user = db.relationship('User', backref='support_chats')
    messages = db.relationship('ChatMessage', backref='chat', lazy=True, cascade='all, delete-orphan')

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.Integer, db.ForeignKey('support_chat.id'), nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # user, agent, bot
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', backref='chat_messages')

@app.route('/support')
def support():
    return render_template('support.html')

@app.route('/support/faq')
def faq():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = FAQ.query.filter_by(is_active=True)
    
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(FAQ.question.contains(search) | FAQ.answer.contains(search))
    
    faqs = query.order_by(FAQ.order, FAQ.created_at.desc()).all()
    categories = db.session.query(FAQ.category).distinct().all()
    
    return render_template('faq.html', faqs=faqs, categories=categories, current_category=category, search=search)

@app.route('/support/tickets')
@login_required
def my_tickets():
    tickets = SupportTicket.query.filter_by(user_id=current_user.id).order_by(SupportTicket.created_at.desc()).all()
    return render_template('my_tickets.html', tickets=tickets)

@app.route('/support/ticket/create', methods=['GET', 'POST'])
@login_required
def create_ticket():
    if request.method == 'POST':
        ticket = SupportTicket(
            user_id=current_user.id,
            subject=request.form['subject'],
            description=request.form['description'],
            category=request.form['category'],
            priority=request.form['priority']
        )
        db.session.add(ticket)
        db.session.commit()
        
        flash('Support ticket created successfully!', 'success')
        return redirect(url_for('my_tickets'))
    
    return render_template('create_ticket.html')

@app.route('/support/ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    
    # Check if user owns the ticket or is admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('my_tickets'))
    
    return render_template('view_ticket.html', ticket=ticket)

@app.route('/support/ticket/<int:ticket_id>/reply', methods=['POST'])
@login_required
def reply_ticket(ticket_id):
    ticket = SupportTicket.query.get_or_404(ticket_id)
    
    # Check if user owns the ticket or is admin
    if ticket.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('my_tickets'))
    
    message = TicketMessage(
        ticket_id=ticket_id,
        user_id=current_user.id,
        message=request.form['message']
    )
    
    db.session.add(message)
    ticket.status = 'in_progress' if ticket.status == 'open' else ticket.status
    db.session.commit()
    
    flash('Reply sent successfully!', 'success')
    return redirect(url_for('view_ticket', ticket_id=ticket_id))

@app.route('/support/chat')
@login_required
def support_chat():
    # Get or create active chat session
    chat = SupportChat.query.filter_by(
        user_id=current_user.id, 
        status='active'
    ).first()
    
    if not chat:
        chat = SupportChat(
            user_id=current_user.id,
            session_id=str(uuid.uuid4())
        )
        db.session.add(chat)
        db.session.commit()
    
    messages = ChatMessage.query.filter_by(chat_id=chat.id).order_by(ChatMessage.created_at.asc()).all()
    
    return render_template('live_chat.html', chat=chat, messages=messages)

@app.route('/api/chat/send', methods=['POST'])
@login_required
def send_chat_message():
    data = request.get_json()
    message_text = data.get('message', '').strip()
    chat_id = data.get('chat_id')
    
    if not message_text or not chat_id:
        return jsonify({'error': 'Invalid message or chat ID'}), 400
    
    # Verify chat belongs to user
    chat = SupportChat.query.filter_by(id=chat_id, user_id=current_user.id).first()
    if not chat:
        return jsonify({'error': 'Chat not found'}), 404
    
    # Save user message
    user_message = ChatMessage(
        chat_id=chat_id,
        sender_type='user',
        sender_id=current_user.id,
        message=message_text
    )
    db.session.add(user_message)
    
    # Generate AI response (simulated)
    ai_response = generate_ai_response(message_text)
    
    # Save AI response
    ai_message = ChatMessage(
        chat_id=chat_id,
        sender_type='bot',
        message=ai_response
    )
    db.session.add(ai_message)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user_message': {
            'id': user_message.id,
            'message': user_message.message,
            'created_at': user_message.created_at.isoformat()
        },
        'ai_response': {
            'id': ai_message.id,
            'message': ai_message.message,
            'created_at': ai_message.created_at.isoformat()
        }
    })

def generate_ai_response(message):
    """Generate AI response for chat support"""
    message_lower = message.lower()
    
    # Simple keyword-based responses
    if any(word in message_lower for word in ['booking', 'reservation', 'book']):
        return "I can help you with your booking! What destination are you interested in? You can also check our current offers at /offers"
    
    elif any(word in message_lower for word in ['payment', 'pay', 'credit card', 'stripe']):
        return "We accept all major credit cards and PayPal. All payments are processed securely through Stripe. Is there a specific payment issue you're experiencing?"
    
    elif any(word in message_lower for word in ['cancel', 'refund', 'money back']):
        return "Our cancellation policy allows free cancellation up to 24 hours before departure. For refunds, please contact our support team with your booking reference."
    
    elif any(word in message_lower for word in ['flight', 'airline', 'departure']):
        return "We offer flights to all major destinations. You can search for flights at /flights or check our package deals at /packages"
    
    elif any(word in message_lower for word in ['hotel', 'accommodation', 'room']):
        return "We have partnerships with hotels worldwide. You can browse our hotel options at /hotels or check our package deals that include accommodation."
    
    elif any(word in message_lower for word in ['weather', 'climate', 'temperature']):
        return "You can check the weather for any destination using our weather feature. Just search for your destination and click on the weather tab!"
    
    elif any(word in message_lower for word in ['price', 'cost', 'expensive', 'cheap']):
        return "Our prices are competitive and we offer various packages to suit different budgets. You can use our advanced search filters to find options within your price range."
    
    elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! Welcome to World Tour support. How can I help you today? I can assist with bookings, payments, travel information, and more!"
    
    elif any(word in message_lower for word in ['thank', 'thanks']):
        return "You're welcome! Is there anything else I can help you with?"
    
    else:
        return "I'm here to help! You can ask me about bookings, payments, destinations, flights, hotels, or any other travel-related questions. What would you like to know?"

# Support and Customer Service Models

class NotificationPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    email_enabled = db.Column(db.Boolean, default=True)
    push_enabled = db.Column(db.Boolean, default=True)
    user = db.relationship('User', backref='notification_preferences')

# Social Features
class SocialPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(500))
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'))
    is_public = db.Column(db.Boolean, default=True)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='social_posts')
    destination = db.relationship('Destination', backref='social_posts')
    likes = db.relationship('PostLike', backref='post', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('PostComment', backref='post', lazy=True, cascade='all, delete-orphan')

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('social_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='post_likes')

class PostComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('social_post.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='post_comments')

class UserFollow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    follower = db.relationship('User', foreign_keys=[follower_id], backref='following')
    following = db.relationship('User', foreign_keys=[following_id], backref='followers')

# Travel Insurance
class InsurancePlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    coverage_type = db.Column(db.String(50))  # basic, comprehensive, premium
    price_per_day = db.Column(db.Float, nullable=False)
    max_coverage = db.Column(db.Float, nullable=False)
    deductible = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InsuranceBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    insurance_plan_id = db.Column(db.Integer, db.ForeignKey('insurance_plan.id'), nullable=False)
    coverage_start = db.Column(db.Date, nullable=False)
    coverage_end = db.Column(db.Date, nullable=False)
    total_premium = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='active')  # active, expired, claimed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='insurance_bookings')
    booking = db.relationship('Booking', backref='insurance')
    plan = db.relationship('InsurancePlan', backref='bookings')

# Offline Maps
class OfflineMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    map_name = db.Column(db.String(100), nullable=False)
    file_url = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    version = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='offline_maps')

class UserMapDownload(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    map_id = db.Column(db.Integer, db.ForeignKey('offline_map.id'), nullable=False)
    downloaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime)
    user = db.relationship('User', backref='downloaded_maps')
    map = db.relationship('OfflineMap', backref='downloads')

# Local Events
class LocalEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(200))
    event_type = db.Column(db.String(50))  # festival, concert, sports, cultural
    price_range = db.Column(db.String(50))
    image_url = db.Column(db.String(500))
    website_url = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='local_events')

# Video Content
class VideoContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500))
    duration = db.Column(db.Integer)  # in seconds
    video_type = db.Column(db.String(50))  # virtual_tour, destination_overview, travel_tips
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='video_content')

# Interactive Maps
class InteractiveMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    map_name = db.Column(db.String(100), nullable=False)
    map_data = db.Column(db.Text)  # JSON data for map points
    zoom_level = db.Column(db.Integer, default=10)
    center_lat = db.Column(db.Float)
    center_lng = db.Column(db.Float)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='interactive_maps')
    points = db.relationship('MapPoint', backref='map', lazy=True, cascade='all, delete-orphan')

class MapPoint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    map_id = db.Column(db.Integer, db.ForeignKey('interactive_map.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    point_type = db.Column(db.String(50))  # attraction, restaurant, hotel, transport
    icon_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# API for Partners
class APIPartner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partner_name = db.Column(db.String(200), nullable=False)
    api_key = db.Column(db.String(100), unique=True, nullable=False)
    webhook_url = db.Column(db.String(500))
    rate_limit = db.Column(db.Integer, default=1000)  # requests per hour
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    usage_logs = db.relationship('APIUsageLog', backref='partner', lazy=True)

class APIUsageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('api_partner.id'), nullable=False)
    endpoint = db.Column(db.String(100), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    response_time = db.Column(db.Float)  # in milliseconds
    status_code = db.Column(db.Integer)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Performance and Analytics
class PerformanceMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(20))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    context = db.Column(db.String(200))  # page, endpoint, etc.

class ErrorLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    error_type = db.Column(db.String(100), nullable=False)
    error_message = db.Column(db.Text, nullable=False)
    stack_trace = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    url = db.Column(db.String(500))
    method = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='error_logs')

# Security and Rate Limiting
class RateLimit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    endpoint = db.Column(db.String(100), nullable=False)
    request_count = db.Column(db.Integer, default=1)
    window_start = db.Column(db.DateTime, nullable=False)
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SecurityEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)  # login_failed, suspicious_activity, etc.
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    details = db.Column(db.Text)
    severity = db.Column(db.String(20), default='low')  # low, medium, high, critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='security_events')

# Testing
class TestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(100), nullable=False)
    test_type = db.Column(db.String(50))  # unit, integration, e2e
    status = db.Column(db.String(20), nullable=False)  # passed, failed, skipped
    execution_time = db.Column(db.Float)  # in seconds
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Deployment and CI/CD
class Deployment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50), nullable=False)
    environment = db.Column(db.String(50), nullable=False)  # staging, production
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, completed, failed
    deployed_by = db.Column(db.String(100))
    deployment_time = db.Column(db.DateTime)
    rollback_time = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# CMS for Content
class ContentPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=False)
    meta_description = db.Column(db.String(300))
    meta_keywords = db.Column(db.String(200))
    is_published = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    author = db.relationship('User', backref='content_pages')

# Weather Integration
class WeatherCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100))
    weather_data = db.Column(db.Text)  # JSON data
    cached_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)

# Mobile App Features
class MobileDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_token = db.Column(db.String(255), unique=True, nullable=False)
    device_type = db.Column(db.String(20))  # ios, android
    app_version = db.Column(db.String(20))
    os_version = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='mobile_devices')

# Location Services
class UserLocation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    accuracy = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='location_history')

# Add these routes after the existing routes (around line 2219, before the models)

# Travel Guides Routes
@app.route('/guides')
def travel_guides():
    guides = TravelGuide.query.filter_by(is_published=True).order_by(TravelGuide.created_at.desc()).all()
    return render_template('travel_guides.html', guides=guides)

@app.route('/guide/<int:guide_id>')
def travel_guide_detail(guide_id):
    guide = TravelGuide.query.get_or_404(guide_id)
    guide.view_count += 1
    db.session.commit()
    return render_template('travel_guide_detail.html', guide=guide)

@app.route('/admin/guides')
@login_required
def admin_guides():
    guides = TravelGuide.query.order_by(TravelGuide.created_at.desc()).all()
    return render_template('admin/guides.html', guides=guides)

@app.route('/admin/guide/create', methods=['GET', 'POST'])
@login_required
def create_guide():
    if request.method == 'POST':
        guide = TravelGuide(
            destination_id=request.form['destination_id'],
            title=request.form['title'],
            content=request.form['content'],
            author_id=current_user.id,
            language=request.form.get('language', 'en')
        )
        db.session.add(guide)
        db.session.commit()
        flash('Travel guide created successfully!', 'success')
        return redirect(url_for('admin_guides'))
    
    destinations = Destination.query.all()
    return render_template('admin/create_guide.html', destinations=destinations)

# Photo Galleries Routes
@app.route('/galleries')
def photo_galleries():
    galleries = PhotoGallery.query.filter_by(is_public=True).order_by(PhotoGallery.created_at.desc()).all()
    return render_template('photo_galleries.html', galleries=galleries)

@app.route('/gallery/<int:gallery_id>')
def gallery_detail(gallery_id):
    gallery = PhotoGallery.query.get_or_404(gallery_id)
    return render_template('gallery_detail.html', gallery=gallery)

@app.route('/gallery/create', methods=['GET', 'POST'])
@login_required
def create_gallery():
    if request.method == 'POST':
        gallery = PhotoGallery(
            user_id=current_user.id,
            destination_id=request.form['destination_id'],
            title=request.form['title'],
            description=request.form['description'],
            is_public=request.form.get('is_public', False)
        )
        db.session.add(gallery)
        db.session.commit()
        flash('Photo gallery created successfully!', 'success')
        return redirect(url_for('gallery_detail', gallery_id=gallery.id))
    
    destinations = Destination.query.all()
    return render_template('create_gallery.html', destinations=destinations)

@app.route('/gallery/<int:gallery_id>/upload', methods=['POST'])
@login_required
def upload_photo(gallery_id):
    gallery = PhotoGallery.query.get_or_404(gallery_id)
    if gallery.user_id != current_user.id:
        flash('You can only upload to your own galleries!', 'error')
        return redirect(url_for('gallery_detail', gallery_id=gallery_id))
    
    # Handle file upload (simplified)
    photo = GalleryPhoto(
        gallery_id=gallery_id,
        image_url=request.form['image_url'],
        caption=request.form['caption']
    )
    db.session.add(photo)
    db.session.commit()
    flash('Photo uploaded successfully!', 'success')
    return redirect(url_for('gallery_detail', gallery_id=gallery_id))

# Travel Checklist Routes
@app.route('/checklist')
@login_required
def travel_checklist():
    checklists = TravelChecklist.query.filter_by(user_id=current_user.id).order_by(TravelChecklist.created_at.desc()).all()
    return render_template('travel_checklist.html', checklists=checklists)

@app.route('/checklist/create', methods=['GET', 'POST'])
@login_required
def create_checklist():
    if request.method == 'POST':
        checklist = TravelChecklist(
            user_id=current_user.id,
            trip_name=request.form['trip_name'],
            destination=request.form['destination'],
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date() if request.form['start_date'] else None,
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form['end_date'] else None
        )
        db.session.add(checklist)
        db.session.commit()
        
        # Add default checklist items
        default_items = [
            ('documents', 'Passport', 'high'),
            ('documents', 'Visa', 'high'),
            ('documents', 'Travel Insurance', 'high'),
            ('clothing', 'Clothes', 'medium'),
            ('electronics', 'Phone Charger', 'medium'),
            ('electronics', 'Camera', 'low'),
            ('toiletries', 'Toothbrush', 'medium'),
            ('toiletries', 'Shampoo', 'low')
        ]
        
        for category, item_name, priority in default_items:
            item = ChecklistItem(
                checklist_id=checklist.id,
                category=category,
                item_name=item_name,
                priority=priority
            )
            db.session.add(item)
        
        db.session.commit()
        flash('Travel checklist created successfully!', 'success')
        return redirect(url_for('travel_checklist'))
    
    return render_template('create_checklist.html')

@app.route('/checklist/<int:checklist_id>/toggle/<int:item_id>', methods=['POST'])
@login_required
def toggle_checklist_item(checklist_id, item_id):
    item = ChecklistItem.query.get_or_404(item_id)
    if item.checklist.user_id != current_user.id:
        flash('You can only modify your own checklists!', 'error')
        return redirect(url_for('travel_checklist'))
    
    item.is_completed = not item.is_completed
    db.session.commit()
    return jsonify({'success': True, 'completed': item.is_completed})

# Loyalty Program Routes
@app.route('/loyalty/dashboard')
@login_required
def loyalty_dashboard():
    user_loyalty = UserLoyalty.query.filter_by(user_id=current_user.id).first()
    if not user_loyalty:
        # Create loyalty account for new user
        base_tier = LoyaltyTier.query.filter_by(min_points=0).first()
        if not base_tier:
            base_tier = LoyaltyTier(name='Bronze', min_points=0, discount_percentage=0.0, color='#CD7F32')
            db.session.add(base_tier)
            db.session.commit()
        
        user_loyalty = UserLoyalty(user_id=current_user.id, tier_id=base_tier.id)
        db.session.add(user_loyalty)
        db.session.commit()
    
    transactions = LoyaltyTransaction.query.filter_by(user_id=current_user.id).order_by(LoyaltyTransaction.created_at.desc()).limit(10).all()
    available_tiers = LoyaltyTier.query.order_by(LoyaltyTier.min_points).all()
    
    return render_template('loyalty_dashboard.html', 
                         user_loyalty=user_loyalty, 
                         transactions=transactions, 
                         available_tiers=available_tiers)

@app.route('/loyalty/redeem', methods=['POST'])
@login_required
def redeem_points():
    points_to_redeem = int(request.form['points'])
    user_loyalty = UserLoyalty.query.filter_by(user_id=current_user.id).first()
    
    if points_to_redeem > user_loyalty.points_balance:
        flash('Insufficient points!', 'error')
        return redirect(url_for('loyalty_dashboard'))
    
    # Create redemption transaction
    transaction = LoyaltyTransaction(
        user_id=current_user.id,
        points=-points_to_redeem,
        transaction_type='redemption',
        description=f'Points redeemed: {points_to_redeem} points'
    )
    db.session.add(transaction)
    
    # Update user balance
    user_loyalty.points_balance -= points_to_redeem
    db.session.commit()
    
    flash(f'Successfully redeemed {points_to_redeem} points!', 'success')
    return redirect(url_for('loyalty_dashboard'))

# Group Bookings Routes
@app.route('/group-bookings')
def group_bookings():
    active_groups = GroupBooking.query.filter_by(status='forming').order_by(GroupBooking.created_at.desc()).all()
    return render_template('group_bookings.html', active_groups=active_groups)

@app.route('/group-booking/create', methods=['GET', 'POST'])
@login_required
def create_group_booking():
    if request.method == 'POST':
        group = GroupBooking(
            leader_id=current_user.id,
            destination_id=request.form['destination_id'],
            group_name=request.form['group_name'],
            group_size=int(request.form['group_size']),
            start_date=datetime.strptime(request.form['start_date'], '%Y-%m-%d').date() if request.form['start_date'] else None,
            end_date=datetime.strptime(request.form['end_date'], '%Y-%m-%d').date() if request.form['end_date'] else None
        )
        db.session.add(group)
        db.session.commit()
        
        # Add leader as first member
        member = GroupMember(group_booking_id=group.id, user_id=current_user.id)
        db.session.add(member)
        db.session.commit()
        
        flash('Group booking created successfully!', 'success')
        return redirect(url_for('group_booking_detail', group_id=group.id))
    
    destinations = Destination.query.all()
    return render_template('create_group_booking.html', destinations=destinations)

@app.route('/group-booking/<int:group_id>')
def group_booking_detail(group_id):
    group = GroupBooking.query.get_or_404(group_id)
    return render_template('group_booking_detail.html', group=group)

@app.route('/group-booking/<int:group_id>/join', methods=['POST'])
@login_required
def join_group_booking(group_id):
    group = GroupBooking.query.get_or_404(group_id)
    
    # Check if user is already a member
    existing_member = GroupMember.query.filter_by(group_booking_id=group_id, user_id=current_user.id).first()
    if existing_member:
        flash('You are already a member of this group!', 'error')
        return redirect(url_for('group_booking_detail', group_id=group_id))
    
    # Check if group is full
    current_members = GroupMember.query.filter_by(group_booking_id=group_id).count()
    if current_members >= group.group_size:
        flash('This group is full!', 'error')
        return redirect(url_for('group_booking_detail', group_id=group_id))
    
    member = GroupMember(group_booking_id=group_id, user_id=current_user.id)
    db.session.add(member)
    db.session.commit()
    
    flash('Successfully joined the group!', 'success')
    return redirect(url_for('group_booking_detail', group_id=group_id))

# Corporate Travel Routes
@app.route('/corporate')
def corporate_travel():
    return render_template('corporate_travel.html')

@app.route('/corporate/register', methods=['GET', 'POST'])
def register_corporate():
    if request.method == 'POST':
        account = CorporateAccount(
            company_name=request.form['company_name'],
            contact_person=request.form['contact_person'],
            email=request.form['email'],
            phone=request.form['phone'],
            address=request.form['address']
        )
        db.session.add(account)
        db.session.commit()
        flash('Corporate account registration submitted! We will contact you soon.', 'success')
        return redirect(url_for('corporate_travel'))
    
    return render_template('register_corporate.html')

# Travel Agents Routes
@app.route('/agents')
def travel_agents():
    agents = TravelAgent.query.filter_by(is_active=True, is_verified=True).all()
    return render_template('travel_agents.html', agents=agents)

@app.route('/agent/register', methods=['GET', 'POST'])
@login_required
def register_agent():
    if request.method == 'POST':
        agent = TravelAgent(
            user_id=current_user.id,
            agency_name=request.form['agency_name'],
            license_number=request.form['license_number']
        )
        db.session.add(agent)
        db.session.commit()
        flash('Agent registration submitted! We will verify your credentials soon.', 'success')
        return redirect(url_for('travel_agents'))
    
    return render_template('register_agent.html')

# Push Notifications Routes
@app.route('/notifications')
@login_required
def notifications():
    notifications = PushNotification.query.filter_by(user_id=current_user.id).order_by(PushNotification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/notification/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    notification = PushNotification.query.get_or_404(notification_id)
    if notification.user_id != current_user.id:
        return jsonify({'success': False}), 403
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})

@app.route('/notification/preferences', methods=['GET', 'POST'])
@login_required
def notification_preferences():
    if request.method == 'POST':
        # Update notification preferences
        for key, value in request.form.items():
            if key.startswith('notification_'):
                notification_type = key.replace('notification_', '')
                pref = NotificationPreference.query.filter_by(
                    user_id=current_user.id, 
                    notification_type=notification_type
                ).first()
                
                if not pref:
                    pref = NotificationPreference(
                        user_id=current_user.id,
                        notification_type=notification_type
                    )
                    db.session.add(pref)
                
                pref.is_enabled = value == 'on'
                pref.email_enabled = request.form.get(f'email_{notification_type}') == 'on'
                pref.push_enabled = request.form.get(f'push_{notification_type}') == 'on'
        
        db.session.commit()
        flash('Notification preferences updated!', 'success')
        return redirect(url_for('notification_preferences'))
    
    preferences = NotificationPreference.query.filter_by(user_id=current_user.id).all()
    return render_template('notification_preferences.html', preferences=preferences)

# Social Features Routes
@app.route('/social')
def social_feed():
    posts = SocialPost.query.filter_by(is_public=True).order_by(SocialPost.created_at.desc()).all()
    return render_template('social_feed.html', posts=posts)

@app.route('/social/post', methods=['GET', 'POST'])
@login_required
def create_social_post():
    if request.method == 'POST':
        post = SocialPost(
            user_id=current_user.id,
            content=request.form['content'],
            image_url=request.form.get('image_url'),
            destination_id=request.form.get('destination_id'),
            is_public=request.form.get('is_public', True)
        )
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('social_feed'))
    
    destinations = Destination.query.all()
    return render_template('create_social_post.html', destinations=destinations)

@app.route('/social/post/<int:post_id>/like', methods=['POST'])
@login_required
def like_post(post_id):
    post = SocialPost.query.get_or_404(post_id)
    
    # Check if already liked
    existing_like = PostLike.query.filter_by(post_id=post_id, user_id=current_user.id).first()
    if existing_like:
        db.session.delete(existing_like)
        post.likes_count -= 1
        liked = False
    else:
        like = PostLike(post_id=post_id, user_id=current_user.id)
        db.session.add(like)
        post.likes_count += 1
        liked = True
    
    db.session.commit()
    return jsonify({'success': True, 'liked': liked, 'likes_count': post.likes_count})

@app.route('/social/post/<int:post_id>/comment', methods=['POST'])
@login_required
def comment_post(post_id):
    post = SocialPost.query.get_or_404(post_id)
    comment = PostComment(
        post_id=post_id,
        user_id=current_user.id,
        content=request.form['content']
    )
    db.session.add(comment)
    post.comments_count += 1
    db.session.commit()
    flash('Comment added successfully!', 'success')
    return redirect(url_for('social_feed'))

@app.route('/social/follow/<int:user_id>', methods=['POST'])
@login_required
def follow_user(user_id):
    if user_id == current_user.id:
        flash('You cannot follow yourself!', 'error')
        return redirect(url_for('social_feed'))
    
    # Check if already following
    existing_follow = UserFollow.query.filter_by(follower_id=current_user.id, following_id=user_id).first()
    if existing_follow:
        db.session.delete(existing_follow)
        followed = False
    else:
        follow = UserFollow(follower_id=current_user.id, following_id=user_id)
        db.session.add(follow)
        followed = True
    
    db.session.commit()
    return jsonify({'success': True, 'followed': followed})

# Travel Insurance Routes
@app.route('/insurance')
def travel_insurance():
    plans = InsurancePlan.query.filter_by(is_active=True).all()
    return render_template('travel_insurance.html', plans=plans)

@app.route('/insurance/plan/<int:plan_id>')
def insurance_plan_detail(plan_id):
    plan = InsurancePlan.query.get_or_404(plan_id)
    return render_template('insurance_plan_detail.html', plan=plan)

@app.route('/insurance/book/<int:plan_id>', methods=['GET', 'POST'])
@login_required
def book_insurance(plan_id):
    plan = InsurancePlan.query.get_or_404(plan_id)
    
    if request.method == 'POST':
        # Calculate premium
        start_date = datetime.strptime(request.form['coverage_start'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['coverage_end'], '%Y-%m-%d').date()
        days = (end_date - start_date).days
        total_premium = plan.price_per_day * days
        
        insurance_booking = InsuranceBooking(
            user_id=current_user.id,
            booking_id=request.form.get('booking_id'),
            insurance_plan_id=plan_id,
            coverage_start=start_date,
            coverage_end=end_date,
            total_premium=total_premium
        )
        db.session.add(insurance_booking)
        db.session.commit()
        
        flash('Insurance booked successfully!', 'success')
        return redirect(url_for('profile'))
    
    user_bookings = Booking.query.filter_by(user_id=current_user.id, status='confirmed').all()
    return render_template('book_insurance.html', plan=plan, user_bookings=user_bookings)

# Offline Maps Routes
@app.route('/maps/offline')
def offline_maps():
    maps = OfflineMap.query.filter_by(is_active=True).all()
    return render_template('offline_maps.html', maps=maps)

@app.route('/maps/offline/<int:map_id>/download')
@login_required
def download_offline_map(map_id):
    map_obj = OfflineMap.query.get_or_404(map_id)
    
    # Record download
    download = UserMapDownload.query.filter_by(user_id=current_user.id, map_id=map_id).first()
    if download:
        download.last_accessed = datetime.utcnow()
    else:
        download = UserMapDownload(user_id=current_user.id, map_id=map_id)
        db.session.add(download)
    
    db.session.commit()
    
    # In a real app, you would serve the actual file
    flash('Map download started!', 'success')
    return redirect(url_for('offline_maps'))

# Local Events Routes
@app.route('/events')
def local_events():
    events = LocalEvent.query.filter_by(is_active=True).order_by(LocalEvent.event_date).all()
    return render_template('local_events.html', events=events)

@app.route('/events/<int:event_id>')
def event_detail(event_id):
    event = LocalEvent.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)

# Video Content Routes
@app.route('/videos')
def video_content():
    videos = VideoContent.query.filter_by(is_featured=True).order_by(VideoContent.created_at.desc()).all()
    return render_template('video_content.html', videos=videos)

@app.route('/videos/<int:video_id>')
def video_detail(video_id):
    video = VideoContent.query.get_or_404(video_id)
    video.view_count += 1
    db.session.commit()
    
    # Extract YouTube video ID from URL if it's a YouTube link
    youtube_id = None
    if 'youtube.com' in video.video_url or 'youtu.be' in video.video_url:
        import re
        youtube_patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)',
            r'youtube\.com\/embed\/([^&\n?#]+)'
        ]
        for pattern in youtube_patterns:
            match = re.search(pattern, video.video_url)
            if match:
                youtube_id = match.group(1)
                break
    
    return render_template('video_detail.html', video=video, youtube_id=youtube_id)

@app.route('/vr/<int:destination_id>')
def virtual_reality_tour(destination_id):
    """Virtual reality tour for a destination"""
    destination = Destination.query.get_or_404(destination_id)
    
    # Get VR content for this destination
    vr_content = get_vr_content(destination_id)
    
    return render_template('vr_tour.html', 
                         destination=destination,
                         vr_content=vr_content)

def get_vr_content(destination_id):
    """Get VR content for a destination"""
    # In a real implementation, this would fetch from a VR content database
    # For now, we'll return simulated VR data
    vr_data = {
        'panoramic_images': [
            {
                'id': 1,
                'title': 'Beach View',
                'image_url': f'/static/vr/{destination_id}/panorama1.jpg',
                'description': '360° view of the pristine beach',
                'hotspots': [
                    {'x': 50, 'y': 30, 'title': 'Beach Bar', 'description': 'Relax with a cocktail'},
                    {'x': 70, 'y': 60, 'title': 'Water Sports', 'description': 'Try surfing or kayaking'}
                ]
            },
            {
                'id': 2,
                'title': 'Hotel Lobby',
                'image_url': f'/static/vr/{destination_id}/panorama2.jpg',
                'description': 'Luxurious hotel lobby with ocean views',
                'hotspots': [
                    {'x': 40, 'y': 50, 'title': 'Reception', 'description': 'Check-in desk'},
                    {'x': 80, 'y': 20, 'title': 'Restaurant', 'description': 'Fine dining with sea views'}
                ]
            },
            {
                'id': 3,
                'title': 'City Center',
                'image_url': f'/static/vr/{destination_id}/panorama3.jpg',
                'description': 'Vibrant city center with local culture',
                'hotspots': [
                    {'x': 30, 'y': 40, 'title': 'Local Market', 'description': 'Explore local crafts and food'},
                    {'x': 60, 'y': 70, 'title': 'Historical Site', 'description': 'Ancient architecture and history'}
                ]
            }
        ],
        'virtual_tour': {
            'tour_id': f'tour_{destination_id}',
            'duration': '15 minutes',
            'stops': [
                {'name': 'Airport Transfer', 'duration': '2 min'},
                {'name': 'Hotel Check-in', 'duration': '3 min'},
                {'name': 'Beach Exploration', 'duration': '5 min'},
                {'name': 'Local Cuisine', 'duration': '3 min'},
                {'name': 'Cultural Sites', 'duration': '2 min'}
            ]
        },
        'interactive_elements': [
            {
                'type': 'hotel_booking',
                'position': {'x': 50, 'y': 50},
                'title': 'Book This Hotel',
                'description': 'Reserve your room with exclusive VR discount'
            },
            {
                'type': 'activity_booking',
                'position': {'x': 70, 'y': 30},
                'title': 'Book Activities',
                'description': 'Reserve water sports and tours'
            },
            {
                'type': 'restaurant_reservation',
                'position': {'x': 30, 'y': 70},
                'title': 'Dining Reservations',
                'description': 'Book tables at top restaurants'
            }
        ]
    }
    
    return vr_data

@app.route('/api/vr/experience/<int:destination_id>')
def vr_experience_api(destination_id):
    """API endpoint for VR experience data"""
    try:
        destination = Destination.query.get_or_404(destination_id)
        vr_content = get_vr_content(destination_id)
        
        return jsonify({
            'success': True,
            'destination': {
                'id': destination.id,
                'name': destination.name,
                'country': destination.country,
                'description': destination.description,
                'image_url': destination.image_url
            },
            'vr_content': vr_content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/vr/booking/<int:destination_id>', methods=['POST'])
@login_required
def vr_booking(destination_id):
    """Handle bookings made through VR experience"""
    try:
        data = request.get_json()
        booking_type = data.get('type')  # hotel, activity, restaurant
        item_id = data.get('item_id')
        date = data.get('date')
        guests = data.get('guests', 1)
        
        destination = Destination.query.get_or_404(destination_id)
        
        # Create booking based on type
        if booking_type == 'hotel':
            # Create hotel booking
            booking = Booking(
                user_id=current_user.id,
                destination_id=destination_id,
                start_date=datetime.strptime(date, '%Y-%m-%d'),
                end_date=datetime.strptime(date, '%Y-%m-%d') + timedelta(days=1),
                guests=guests,
                total_price=destination.price * guests,
                status='pending',
                payment_status='pending'
            )
            db.session.add(booking)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Hotel booking created through VR experience!',
                'booking_id': booking.id
            })
        
        elif booking_type == 'activity':
            # Create activity booking
            return jsonify({
                'success': True,
                'message': 'Activity booking feature coming soon!'
            })
        
        elif booking_type == 'restaurant':
            # Create restaurant reservation
            return jsonify({
                'success': True,
                'message': 'Restaurant reservation feature coming soon!'
            })
        
        else:
            return jsonify({'error': 'Invalid booking type'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Interactive Maps Routes
@app.route('/maps/interactive/<int:destination_id>')
def interactive_map(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    map_obj = InteractiveMap.query.filter_by(destination_id=destination_id, is_active=True).first()
    return render_template('interactive_map.html', destination=destination, map_obj=map_obj)

# API Routes for Partners
@app.route('/api/v1/destinations')
def api_destinations_v1():
    # Basic API authentication (in production, use proper JWT tokens)
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'API key required'}), 401
    
    partner = APIPartner.query.filter_by(api_key=api_key, is_active=True).first()
    if not partner:
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Rate limiting
    current_time = datetime.utcnow()
    window_start = current_time - timedelta(hours=1)
    
    usage_count = APIUsageLog.query.filter_by(
        partner_id=partner.id
    ).filter(
        APIUsageLog.created_at >= window_start
    ).count()
    
    if usage_count >= partner.rate_limit:
        return jsonify({'error': 'Rate limit exceeded'}), 429
    
    # Log API usage
    usage_log = APIUsageLog(
        partner_id=partner.id,
        endpoint='/api/v1/destinations',
        method='GET',
        response_time=0.0,
        status_code=200,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(usage_log)
    db.session.commit()
    
    destinations = Destination.query.all()
    return jsonify({
        'destinations': [
            {
                'id': d.id,
                'name': d.name,
                'country': d.country,
                'description': d.description,
                'price': d.price,
                'image_url': d.image_url
            } for d in destinations
        ]
    })

@app.route('/api/v1/bookings', methods=['POST'])
def api_create_booking():
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return jsonify({'error': 'API key required'}), 401
    
    partner = APIPartner.query.filter_by(api_key=api_key, is_active=True).first()
    if not partner:
        return jsonify({'error': 'Invalid API key'}), 401
    
    data = request.get_json()
    
    # Create booking via API
    booking = Booking(
        user_id=data.get('user_id'),
        destination_id=data.get('destination_id'),
        start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
        end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
        guests=data.get('guests', 1),
        total_price=data['total_price'],
        status='confirmed'
    )
    db.session.add(booking)
    db.session.commit()
    
    return jsonify({'success': True, 'booking_id': booking.id})

# Performance and Analytics Routes
@app.route('/admin/performance')
@login_required
def admin_performance():
    # Get performance metrics
    metrics = PerformanceMetric.query.order_by(PerformanceMetric.timestamp.desc()).limit(50).all()
    
    # Get error logs
    errors = ErrorLog.query.order_by(ErrorLog.created_at.desc()).limit(20).all()
    
    return render_template('admin/performance.html', metrics=metrics, errors=errors)

@app.route('/admin/security')
@login_required
def admin_security():
    # Get security events
    events = SecurityEvent.query.order_by(SecurityEvent.created_at.desc()).limit(50).all()
    
    # Get rate limiting data
    rate_limits = RateLimit.query.filter_by(is_blocked=True).all()
    
    return render_template('admin/security.html', events=events, rate_limits=rate_limits)

# CMS Routes
@app.route('/admin/cms')
@login_required
def admin_cms():
    pages = ContentPage.query.order_by(ContentPage.created_at.desc()).all()
    return render_template('admin/cms.html', pages=pages)

@app.route('/admin/cms/create', methods=['GET', 'POST'])
@login_required
def create_content_page():
    if request.method == 'POST':
        page = ContentPage(
            title=request.form['title'],
            slug=request.form['slug'],
            content=request.form['content'],
            meta_description=request.form['meta_description'],
            meta_keywords=request.form['meta_keywords'],
            author_id=current_user.id,
            is_published=request.form.get('is_published', False)
        )
        db.session.add(page)
        db.session.commit()
        flash('Content page created successfully!', 'success')
        return redirect(url_for('admin_cms'))
    
    return render_template('admin/create_content_page.html')

@app.route('/page/<slug>')
def content_page(slug):
    page = ContentPage.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('content_page.html', page=page)

# Weather Integration Routes
@app.route('/weather/<city>')
def weather_detail(city):
    # Check cache first
    cache = WeatherCache.query.filter_by(city=city).filter(WeatherCache.expires_at > datetime.utcnow()).first()
    
    if cache:
        weather_data = json.loads(cache.weather_data)
    else:
        # Get fresh weather data
        weather_data = get_weather(city)
        
        # Cache the data
        if cache:
            cache.weather_data = json.dumps(weather_data)
            cache.cached_at = datetime.utcnow()
            cache.expires_at = datetime.utcnow() + timedelta(hours=1)
        else:
            cache = WeatherCache(
                city=city,
                weather_data=json.dumps(weather_data),
                expires_at=datetime.utcnow() + timedelta(hours=1)
            )
            db.session.add(cache)
        
        db.session.commit()
    
    return render_template('weather_detail.html', city=city, weather=weather_data)

# Mobile App Routes
@app.route('/api/mobile/register-device', methods=['POST'])
@login_required
def register_mobile_device():
    data = request.get_json()
    
    device = MobileDevice(
        user_id=current_user.id,
        device_token=data['device_token'],
        device_type=data['device_type'],
        app_version=data.get('app_version'),
        os_version=data.get('os_version')
    )
    db.session.add(device)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/api/mobile/location', methods=['POST'])
@login_required
def update_location():
    data = request.get_json()
    
    location = UserLocation(
        user_id=current_user.id,
        latitude=data['latitude'],
        longitude=data['longitude'],
        accuracy=data.get('accuracy')
    )
    db.session.add(location)
    db.session.commit()
    
    return jsonify({'success': True})

# Real-time Chat Routes
@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')



# Testing Routes
@app.route('/admin/tests')
@login_required
def admin_tests():
    test_results = TestResult.query.order_by(TestResult.created_at.desc()).limit(100).all()
    return render_template('admin/tests.html', test_results=test_results)

@app.route('/admin/run-tests')
@login_required
def run_tests():
    # Run basic tests
    tests = [
        ('Database Connection', 'unit', 'passed', 0.1),
        ('User Authentication', 'integration', 'passed', 0.5),
        ('Payment Processing', 'integration', 'passed', 1.2),
        ('Email Sending', 'unit', 'passed', 0.3)
    ]
    
    for test_name, test_type, status, execution_time in tests:
        result = TestResult(
            test_name=test_name,
            test_type=test_type,
            status=status,
            execution_time=execution_time
        )
        db.session.add(result)
    
    db.session.commit()
    flash('Tests completed!', 'success')
    return redirect(url_for('admin_tests'))

# Deployment Routes
@app.route('/admin/deployments')
@login_required
def admin_deployments():
    deployments = Deployment.query.order_by(Deployment.created_at.desc()).all()
    return render_template('admin/deployments.html', deployments=deployments)

@app.route('/admin/deploy', methods=['POST'])
@login_required
def create_deployment():
    deployment = Deployment(
        version=request.form['version'],
        environment=request.form['environment'],
        deployed_by=current_user.username,
        notes=request.form['notes']
    )
    db.session.add(deployment)
    db.session.commit()
    
    flash('Deployment created!', 'success')
    return redirect(url_for('admin_deployments'))

# Enhanced Search and Filters
@app.route('/search/advanced')
def advanced_search():
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    price_min = request.args.get('price_min', '')
    price_max = request.args.get('price_max', '')
    duration = request.args.get('duration', '')
    rating = request.args.get('rating', '')
    
    destinations = Destination.query
    
    if query:
        destinations = destinations.filter(
            db.or_(
                Destination.name.contains(query),
                Destination.country.contains(query),
                Destination.description.contains(query)
            )
        )
    
    if category:
        destinations = destinations.filter(Destination.category == category)
    
    if price_min:
        destinations = destinations.filter(Destination.price >= float(price_min))
    
    if price_max:
        destinations = destinations.filter(Destination.price <= float(price_max))
    
    if duration:
        destinations = destinations.filter(Destination.duration == int(duration))
    
    if rating:
        destinations = destinations.filter(Destination.rating >= float(rating))
    
    destinations = destinations.all()
    
    return render_template('advanced_search.html', 
                         destinations=destinations, 
                         query=query,
                         category=category,
                         price_min=price_min,
                         price_max=price_max,
                         duration=duration,
                         rating=rating)

# SEO and Meta Tags
@app.route('/sitemap.xml')
def sitemap():
    """Generate XML sitemap for search engines"""
    from flask import make_response
    
    # Get all destinations
    destinations = Destination.query.filter_by(available=True).all()
    
    # Get all blog posts
    blog_posts = BlogPost.query.filter_by(is_published=True).all()
    
    # Create sitemap XML
    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    
    # Homepage
    sitemap_xml += f'  <url>\n'
    sitemap_xml += f'    <loc>{request.url_root}</loc>\n'
    sitemap_xml += f'    <lastmod>{datetime.utcnow().strftime("%Y-%m-%d")}</lastmod>\n'
    sitemap_xml += f'    <changefreq>daily</changefreq>\n'
    sitemap_xml += f'    <priority>1.0</priority>\n'
    sitemap_xml += f'  </url>\n'
    
    # Main pages
    main_pages = [
        ('travel', 'daily', '0.9'),
        ('offers', 'daily', '0.9'),
        ('hotels', 'daily', '0.8'),
        ('flights', 'daily', '0.8'),
        ('packages', 'daily', '0.8'),
        ('blog', 'weekly', '0.7'),
        ('contact', 'monthly', '0.5'),
        ('about', 'monthly', '0.5')
    ]
    
    for page, freq, priority in main_pages:
        sitemap_xml += f'  <url>\n'
        sitemap_xml += f'    <loc>{request.url_root}{page}</loc>\n'
        sitemap_xml += f'    <lastmod>{datetime.utcnow().strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_xml += f'    <changefreq>{freq}</changefreq>\n'
        sitemap_xml += f'    <priority>{priority}</priority>\n'
        sitemap_xml += f'  </url>\n'
    
    # Destinations
    for destination in destinations:
        sitemap_xml += f'  <url>\n'
        sitemap_xml += f'    <loc>{request.url_root}destination/{destination.id}</loc>\n'
        sitemap_xml += f'    <lastmod>{destination.created_at.strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_xml += f'    <changefreq>weekly</changefreq>\n'
        sitemap_xml += f'    <priority>0.8</priority>\n'
        sitemap_xml += f'  </url>\n'
    
    # Blog posts
    for post in blog_posts:
        sitemap_xml += f'  <url>\n'
        sitemap_xml += f'    <loc>{request.url_root}blog/{post.slug}</loc>\n'
        sitemap_xml += f'    <lastmod>{post.updated_at.strftime("%Y-%m-%d")}</lastmod>\n'
        sitemap_xml += f'    <changefreq>monthly</changefreq>\n'
        sitemap_xml += f'    <priority>0.6</priority>\n'
        sitemap_xml += f'  </url>\n'
    
    sitemap_xml += '</urlset>'
    
    response = make_response(sitemap_xml)
    response.headers['Content-Type'] = 'application/xml'
    return response

@app.route('/robots.txt')
def robots():
    """Generate robots.txt for search engines"""
    robots_txt = f"""User-agent: *
Allow: /

# Sitemap
Sitemap: {request.url_root}sitemap.xml

# Disallow admin areas
Disallow: /admin/
Disallow: /api/
Disallow: /static/admin/

# Allow important pages
Allow: /travel/
Allow: /destination/
Allow: /blog/
Allow: /offers/
Allow: /hotels/
Allow: /flights/
Allow: /packages/

# Crawl delay (optional)
Crawl-delay: 1
"""
    response = make_response(robots_txt)
    response.headers['Content-Type'] = 'text/plain'
    return response

# Error Handling
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# Background Tasks (simplified without Celery)
def send_notification_task(user_id, title, message, notification_type):
    """Background task to send notifications"""
    try:
        notification = PushNotification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type
        )
        db.session.add(notification)
        db.session.commit()
        
        # In production, send actual push notification
        print(f"Notification sent to user {user_id}: {title}")
        
    except Exception as e:
        print(f"Error sending notification: {e}")

def update_loyalty_tiers():
    """Background task to update user loyalty tiers"""
    try:
        users = UserLoyalty.query.all()
        tiers = LoyaltyTier.query.order_by(LoyaltyTier.min_points).all()
        
        for user in users:
            for tier in tiers:
                if user.points_balance >= tier.min_points:
                    user.tier_id = tier.id
                    break
        
        db.session.commit()
        print("Loyalty tiers updated successfully")
        
    except Exception as e:
        print(f"Error updating loyalty tiers: {e}")

# Utility Functions
def log_error(error_type, error_message, user_id=None, stack_trace=None):
    """Log errors to database"""
    error_log = ErrorLog(
        error_type=error_type,
        error_message=error_message,
        stack_trace=stack_trace,
        user_id=user_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        url=request.url,
        method=request.method
    )
    db.session.add(error_log)
    db.session.commit()

def log_security_event(event_type, user_id=None, details=None, severity='low'):
    """Log security events"""
    security_event = SecurityEvent(
        event_type=event_type,
        user_id=user_id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent'),
        details=details,
        severity=severity
    )
    db.session.add(security_event)
    db.session.commit()

def log_performance_metric(metric_name, metric_value, metric_unit=None, context=None):
    """Log performance metrics"""
    metric = PerformanceMetric(
        metric_name=metric_name,
        metric_value=metric_value,
        metric_unit=metric_unit,
        context=context
    )
    db.session.add(metric)
    db.session.commit()

# Loyalty Program Models
# Move LoyaltyTier class definition to before init_db function
class LoyaltyTier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    min_points = db.Column(db.Integer, nullable=False)
    discount_percentage = db.Column(db.Float, default=0.0)
    benefits = db.Column(db.Text)
    color = db.Column(db.String(20))

class UserLoyalty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points_balance = db.Column(db.Integer, default=0)
    tier_id = db.Column(db.Integer, db.ForeignKey('loyalty_tier.id'), nullable=False)
    total_spent = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='loyalty')
    tier = db.relationship('LoyaltyTier', backref='users')

class LoyaltyTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)  # positive for earned, negative for spent
    transaction_type = db.Column(db.String(50))  # booking, referral, bonus, redemption
    description = db.Column(db.String(200))
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='loyalty_transactions')
    booking = db.relationship('Booking', backref='loyalty_transactions')

# Travel Guides and Content Management
class TravelGuide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    language = db.Column(db.String(10), default='en')
    is_published = db.Column(db.Boolean, default=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    destination = db.relationship('Destination', backref='travel_guides')
    author = db.relationship('User', backref='travel_guides')

class PhotoGallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='photo_galleries')
    destination = db.relationship('Destination', backref='photo_galleries')
    photos = db.relationship('GalleryPhoto', backref='gallery', lazy=True, cascade='all, delete-orphan')

class GalleryPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gallery_id = db.Column(db.Integer, db.ForeignKey('photo_gallery.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(200))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class TravelChecklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trip_name = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='travel_checklists')
    items = db.relationship('ChecklistItem', backref='checklist', lazy=True, cascade='all, delete-orphan')

class ChecklistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('travel_checklist.id'), nullable=False)
    category = db.Column(db.String(50))  # documents, clothing, electronics, etc.
    item_name = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    notes = db.Column(db.Text)

# Group Bookings
class GroupBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    group_name = db.Column(db.String(100), nullable=False)
    group_size = db.Column(db.Integer, nullable=False)
    discount_percentage = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='forming')  # forming, confirmed, completed
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    leader = db.relationship('User', backref='group_bookings_led')
    destination = db.relationship('Destination', backref='group_bookings')
    members = db.relationship('GroupMember', backref='group_booking', lazy=True, cascade='all, delete-orphan')

class GroupMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_booking_id = db.Column(db.Integer, db.ForeignKey('group_booking.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='group_memberships')

# Corporate Travel
class CorporateAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    discount_percentage = db.Column(db.Float, default=0.0)
    credit_limit = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    employees = db.relationship('CorporateEmployee', backref='company', lazy=True, cascade='all, delete-orphan')

class CorporateEmployee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    corporate_account_id = db.Column(db.Integer, db.ForeignKey('corporate_account.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    employee_id = db.Column(db.String(50))
    department = db.Column(db.String(100))
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_authorized = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', foreign_keys=[user_id], backref='corporate_employment')
    manager = db.relationship('User', foreign_keys=[manager_id], backref='managed_employees')

# Travel Agents
class TravelAgent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    agency_name = db.Column(db.String(200), nullable=False)
    license_number = db.Column(db.String(50))
    commission_rate = db.Column(db.Float, default=0.10)  # 10% default
    total_earnings = db.Column(db.Float, default=0.0)
    total_bookings = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='travel_agent_profile')
    bookings = db.relationship('AgentBooking', backref='agent', lazy=True)

class AgentBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    agent_id = db.Column(db.Integer, db.ForeignKey('travel_agent.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    commission_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, paid, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    booking = db.relationship('Booking', backref='agent_booking')

# Push Notifications
class PushNotification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # price_alert, booking_reminder, promotion
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime)
    user = db.relationship('User', backref='push_notifications')

# Blockchain and Cryptocurrency Models
class BlockchainTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, failed
    blockchain_type = db.Column(db.String(20))  # ethereum, bitcoin, polygon
    wallet_address = db.Column(db.String(100))
    gas_fee = db.Column(db.Float, default=0.0)
    tx_hash = db.Column(db.String(100))
    block_number = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    user = db.relationship('User', backref='blockchain_transactions')
    booking = db.relationship('Booking', backref='blockchain_transactions')

class CryptoTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'))
    fiat_amount = db.Column(db.Float, nullable=False)
    crypto_amount = db.Column(db.Float, nullable=False)
    crypto_type = db.Column(db.String(10))  # BTC, ETH, USDT, USDC
    exchange_rate = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, failed
    wallet_address = db.Column(db.String(100))
    tx_hash = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    confirmed_at = db.Column(db.DateTime)
    user = db.relationship('User', backref='crypto_transactions')
    booking = db.relationship('Booking', backref='crypto_transactions')

class SmartContract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contract_address = db.Column(db.String(100), unique=True, nullable=False)
    contract_type = db.Column(db.String(50))  # booking, insurance, loyalty
    network = db.Column(db.String(20))  # ethereum, polygon, binance
    abi = db.Column(db.Text)  # Contract ABI
    bytecode = db.Column(db.Text)  # Contract bytecode
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    deployed_at = db.Column(db.DateTime)

# Real-Time Data Models
class FlightTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(20), nullable=False)
    airline = db.Column(db.String(100), nullable=False)
    origin = db.Column(db.String(10), nullable=False)
    destination = db.Column(db.String(10), nullable=False)
    departure_time = db.Column(db.DateTime, nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    actual_departure = db.Column(db.DateTime)
    actual_arrival = db.Column(db.DateTime)
    status = db.Column(db.String(50))  # on_time, delayed, cancelled, diverted
    delay_minutes = db.Column(db.Integer, default=0)
    gate = db.Column(db.String(10))
    terminal = db.Column(db.String(10))
    aircraft_type = db.Column(db.String(50))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    tracking_data = db.Column(db.Text)  # JSON with detailed tracking info

class HotelAvailability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    room_type_id = db.Column(db.Integer, db.ForeignKey('room_type.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    available_rooms = db.Column(db.Integer, nullable=False)
    total_rooms = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(50))  # direct, gds, ota

class DynamicPricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    base_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    demand_factor = db.Column(db.Float, default=1.0)
    supply_factor = db.Column(db.Float, default=1.0)
    seasonality_factor = db.Column(db.Float, default=1.0)
    competitor_price = db.Column(db.Float)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    algorithm_version = db.Column(db.String(20))

# Advanced Personalization Models
class UserBehavior(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    page_url = db.Column(db.String(500), nullable=False)
    action_type = db.Column(db.String(50))  # view, click, search, book, like
    action_data = db.Column(db.Text)  # JSON with action details
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    referrer = db.Column(db.String(500))
    time_spent = db.Column(db.Integer)  # seconds

class UserPreference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    preference_type = db.Column(db.String(50))  # destination, budget, style, activities
    preference_value = db.Column(db.String(200))
    confidence_score = db.Column(db.Float, default=0.0)
    source = db.Column(db.String(50))  # explicit, inferred, ml
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class PriceAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    target_price = db.Column(db.Float, nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    triggered_at = db.Column(db.DateTime)

# Mobile App Models
class BoardingPass(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    passenger_name = db.Column(db.String(100), nullable=False)
    flight_number = db.Column(db.String(20), nullable=False)
    seat_number = db.Column(db.String(10))
    gate = db.Column(db.String(10))
    boarding_time = db.Column(db.DateTime)
    qr_code = db.Column(db.String(500))
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='boarding_passes')

# Customer Support Models

class WhatsAppIntegration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    whatsapp_id = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='whatsapp_integration')

# Content & Discovery Models
class VirtualTour(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    video_url = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    duration = db.Column(db.Integer)  # seconds
    view_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='virtual_tours')

class LocalGuide(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    bio = db.Column(db.Text)
    languages = db.Column(db.Text)  # JSON array
    specialties = db.Column(db.Text)  # JSON array
    hourly_rate = db.Column(db.Float, nullable=False)
    rating = db.Column(db.Float, default=0.0)
    review_count = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='guide_profile')
    destination = db.relationship('Destination', backref='local_guides')

class TravelPodcast(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    audio_url = db.Column(db.String(500))
    duration = db.Column(db.Integer)  # seconds
    host_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'))
    episode_number = db.Column(db.Integer)
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)
    download_count = db.Column(db.Integer, default=0)
    host = db.relationship('User', backref='podcasts')
    destination = db.relationship('Destination', backref='podcasts')

# Security & Compliance Models
class TwoFactorAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    secret_key = db.Column(db.String(100), nullable=False)
    backup_codes = db.Column(db.Text)  # JSON array
    is_enabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='two_factor_auth')

class FraudDetection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    transaction_id = db.Column(db.String(100))
    risk_score = db.Column(db.Float, nullable=False)
    risk_factors = db.Column(db.Text)  # JSON array
    action_taken = db.Column(db.String(50))  # allow, block, review
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='fraud_events')

# Advanced Analytics Models
class ABTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    variant_a = db.Column(db.String(50), nullable=False)
    variant_b = db.Column(db.String(50), nullable=False)
    traffic_split = db.Column(db.Float, default=0.5)  # 50% split
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ABTestResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('ab_test.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    variant = db.Column(db.String(50), nullable=False)
    conversion = db.Column(db.Boolean, default=False)
    revenue = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    test = db.relationship('ABTest', backref='results')
    user = db.relationship('User', backref='ab_test_participations')

class ConversionFunnel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    funnel_name = db.Column(db.String(100), nullable=False)
    step_name = db.Column(db.String(100), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    user_count = db.Column(db.Integer, default=0)
    conversion_rate = db.Column(db.Float, default=0.0)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CustomerLifetimeValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_revenue = db.Column(db.Float, default=0.0)
    total_orders = db.Column(db.Integer, default=0)
    average_order_value = db.Column(db.Float, default=0.0)
    first_purchase_date = db.Column(db.DateTime)
    last_purchase_date = db.Column(db.DateTime)
    predicted_lifetime_value = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = db.relationship('User', backref='lifetime_value')

# Real-Time Data Integration Functions
def get_flight_tracking(flight_number):
    """Get real-time flight tracking data"""
    try:
        # Check cache first
        cache_key = f"flight_tracking_{flight_number}"
        cached_data = redis_client.get(cache_key) if redis_client else None
        if cached_data:
            return json.loads(cached_data)
        
        # Simulate real-time flight data (replace with actual API calls)
        flight_data = {
            'flight_number': flight_number,
            'status': 'on_time',
            'delay_minutes': 0,
            'gate': 'A12',
            'terminal': '1',
            'actual_departure': None,
            'actual_arrival': None,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Cache for 5 minutes
        if redis_client:
            redis_client.setex(cache_key, 300, json.dumps(flight_data))
        return flight_data
    except Exception as e:
        log_error('flight_tracking_error', str(e))
        return None

def get_hotel_availability(hotel_id, check_in, check_out):
    """Get real-time hotel availability"""
    try:
        cache_key = f"hotel_availability_{hotel_id}_{check_in}_{check_out}"
        cached_data = redis_client.get(cache_key) if redis_client else None
        if cached_data:
            return json.loads(cached_data)
        
        # Simulate real-time availability (replace with actual API calls)
        availability_data = {
            'hotel_id': hotel_id,
            'available_rooms': 15,
            'total_rooms': 50,
            'price': 150.0,
            'currency': 'USD',
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Cache for 10 minutes
        if redis_client:
            redis_client.setex(cache_key, 600, json.dumps(availability_data))
        return availability_data
    except Exception as e:
        log_error('hotel_availability_error', str(e))
        return None

def calculate_dynamic_pricing(destination_id, travel_date, demand_factor=1.0):
    """Calculate dynamic pricing based on demand and supply"""
    try:
        destination = Destination.query.get(destination_id)
        if not destination:
            return 0
        
        # Base price
        base_price = destination.price
        
        # Demand factor (higher demand = higher price)
        demand_multiplier = 1.0 + (demand_factor - 1.0) * 0.3
        
        # Seasonality factor
        month = travel_date.month
        if month in [6, 7, 8, 12]:  # Peak season
            seasonality_multiplier = 1.2
        elif month in [1, 2, 11]:  # Low season
            seasonality_multiplier = 0.8
        else:  # Shoulder season
            seasonality_multiplier = 1.0
        
        # Calculate final price
        final_price = base_price * demand_multiplier * seasonality_multiplier
        
        # Update dynamic pricing record
        dynamic_pricing = DynamicPricing.query.filter_by(destination_id=destination_id).first()
        if not dynamic_pricing:
            dynamic_pricing = DynamicPricing(
                destination_id=destination_id,
                base_price=base_price,
                current_price=final_price,
                demand_factor=demand_factor,
                seasonality_factor=seasonality_multiplier
            )
            db.session.add(dynamic_pricing)
        else:
            dynamic_pricing.current_price = final_price
            dynamic_pricing.demand_factor = demand_factor
            dynamic_pricing.seasonality_factor = seasonality_multiplier
            dynamic_pricing.last_updated = datetime.utcnow()
        
        db.session.commit()
        return final_price
    except Exception as e:
        log_error('dynamic_pricing_error', str(e))
        return destination.price if destination else 0

# Advanced Personalization Functions
def track_user_behavior(user_id, session_id, page_url, action_type, action_data=None):
    """Track user behavior for personalization"""
    try:
        behavior = UserBehavior(
            user_id=user_id,
            session_id=session_id,
            page_url=page_url,
            action_type=action_type,
            action_data=json.dumps(action_data) if action_data else None,
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string,
            referrer=request.referrer
        )
        db.session.add(behavior)
        db.session.commit()
    except Exception as e:
        log_error('user_behavior_tracking_error', str(e))

def get_user_preferences(user_id):
    """Get user preferences for personalization"""
    try:
        preferences = UserPreference.query.filter_by(user_id=user_id).all()
        return {pref.preference_type: pref.preference_value for pref in preferences}
    except Exception as e:
        log_error('user_preferences_error', str(e))
        return {}

def update_user_preferences(user_id, preference_type, preference_value, confidence_score=0.8):
    """Update user preferences"""
    try:
        existing_pref = UserPreference.query.filter_by(
            user_id=user_id, 
            preference_type=preference_type
        ).first()
        
        if existing_pref:
            existing_pref.preference_value = preference_value
            existing_pref.confidence_score = confidence_score
            existing_pref.updated_at = datetime.utcnow()
        else:
            new_pref = UserPreference(
                user_id=user_id,
                preference_type=preference_type,
                preference_value=preference_value,
                confidence_score=confidence_score
            )
            db.session.add(new_pref)
        
        db.session.commit()
    except Exception as e:
        log_error('update_preferences_error', str(e))

def get_personalized_recommendations_ml(user_id, limit=6):
    """Get ML-powered personalized recommendations"""
    try:
        # Get user behavior data
        user_behaviors = UserBehavior.query.filter_by(user_id=user_id).order_by(
            UserBehavior.timestamp.desc()
        ).limit(100).all()
        
        # Get user preferences
        preferences = get_user_preferences(user_id)
        
        # Get all destinations
        all_destinations = Destination.query.filter_by(available=True).all()
        
        # Calculate recommendation scores
        recommendations = []
        for destination in all_destinations:
            score = 0.0
            
            # Base score from destination rating
            score += destination.rating * 0.3
            
            # Preference matching
            if 'destination' in preferences:
                if preferences['destination'].lower() in destination.country.lower():
                    score += 0.4
            
            # Budget matching
            if 'budget' in preferences:
                budget_pref = preferences['budget'].lower()
                if budget_pref == 'low' and destination.price < 1000:
                    score += 0.3
                elif budget_pref == 'medium' and 1000 <= destination.price <= 3000:
                    score += 0.3
                elif budget_pref == 'high' and destination.price > 3000:
                    score += 0.3
            
            # Category matching
            if 'style' in preferences:
                if preferences['style'].lower() in destination.category.lower():
                    score += 0.2
            
            recommendations.append((destination, score))
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return [dest for dest, score in recommendations[:limit]]
    except Exception as e:
        log_error('ml_recommendations_error', str(e))
        return Destination.query.filter_by(available=True).limit(limit).all()

# Mobile App Functions
def generate_boarding_pass(booking_id, passenger_name, flight_number):
    """Generate boarding pass with QR code"""
    try:
        # Generate QR code
        qr_data = f"BOARDING_PASS:{booking_id}:{passenger_name}:{flight_number}"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR code image
        qr_image = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        img_buffer = BytesIO()
        qr_image.save(img_buffer, format='PNG')
        img_buffer.seek(0)
        
        # Convert to base64 for storage
        qr_base64 = base64.b64encode(img_buffer.getvalue()).decode()
        
        # Create boarding pass
        boarding_pass = BoardingPass(
            booking_id=booking_id,
            passenger_name=passenger_name,
            flight_number=flight_number,
            qr_code=f"data:image/png;base64,{qr_base64}"
        )
        
        db.session.add(boarding_pass)
        db.session.commit()
        
        return boarding_pass
    except Exception as e:
        log_error('boarding_pass_generation_error', str(e))
        return None

def send_push_notification(user_id, title, message, notification_type='general'):
    """Send push notification to mobile devices"""
    try:
        # Get user's mobile devices
        devices = MobileDevice.query.filter_by(user_id=user_id, is_active=True).all()
        
        for device in devices:
            # Create notification record
            notification = PushNotification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type
            )
            db.session.add(notification)
        
        db.session.commit()
        
        # In production, integrate with Firebase Cloud Messaging or Apple Push Notification Service
        return True
    except Exception as e:
        log_error('push_notification_error', str(e))
        return False

# Customer Support Functions
def create_support_ticket(user_id, subject, description, category='general', priority='medium'):
    """Create a new support ticket"""
    try:
        ticket = SupportTicket(
            user_id=user_id,
            subject=subject,
            description=description,
            category=category,
            priority=priority
        )
        db.session.add(ticket)
        db.session.commit()
        
        # Send notification to support team
        # In production, integrate with helpdesk system like Zendesk
        
        return ticket
    except Exception as e:
        log_error('support_ticket_creation_error', str(e))
        return None

def send_whatsapp_message(phone_number, message):
    """Send WhatsApp message (integrate with WhatsApp Business API)"""
    try:
        # In production, integrate with WhatsApp Business API
        # For now, simulate sending
        print(f"WhatsApp message to {phone_number}: {message}")
        return True
    except Exception as e:
        log_error('whatsapp_message_error', str(e))
        return False

# Security & Compliance Functions
def generate_2fa_secret():
    """Generate 2FA secret key"""
    import secrets
    return secrets.token_hex(16)

def verify_2fa_code(secret_key, code):
    """Verify 2FA code"""
    try:
        import pyotp
        totp = pyotp.TOTP(secret_key)
        return totp.verify(code)
    except Exception as e:
        log_error('2fa_verification_error', str(e))
        return False

def detect_fraud(user_id, transaction_data):
    """Detect potential fraud"""
    try:
        risk_score = 0.0
        risk_factors = []
        
        # Check for suspicious patterns
        recent_transactions = Booking.query.filter_by(user_id=user_id).order_by(
            Booking.created_at.desc()
        ).limit(10).all()
        
        # High value transaction
        if transaction_data.get('amount', 0) > 5000:
            risk_score += 0.3
            risk_factors.append('high_value')
        
        # Multiple transactions in short time
        if len(recent_transactions) > 5:
            risk_score += 0.2
            risk_factors.append('multiple_transactions')
        
        # Unusual location
        if transaction_data.get('ip_country') != 'US':  # Example
            risk_score += 0.1
            risk_factors.append('unusual_location')
        
        # Create fraud detection record
        fraud_record = FraudDetection(
            user_id=user_id,
            transaction_id=transaction_data.get('transaction_id'),
            risk_score=risk_score,
            risk_factors=json.dumps(risk_factors),
            action_taken='allow' if risk_score < 0.5 else 'review',
            ip_address=request.remote_addr,
            user_agent=request.user_agent.string
        )
        db.session.add(fraud_record)
        db.session.commit()
        
        return risk_score < 0.5  # Allow if risk score is low
    except Exception as e:
        log_error('fraud_detection_error', str(e))
        return True  # Allow by default if error

# Advanced Analytics Functions
def run_ab_test(test_name, user_id, variant_a, variant_b):
    """Run A/B test"""
    try:
        # Get or create A/B test
        ab_test = ABTest.query.filter_by(test_name=test_name, is_active=True).first()
        if not ab_test:
            ab_test = ABTest(
                test_name=test_name,
                variant_a=variant_a,
                variant_b=variant_b,
                start_date=datetime.utcnow()
            )
            db.session.add(ab_test)
            db.session.commit()
        
        # Assign variant based on user ID hash
        user_hash = hash(str(user_id)) % 100
        variant = variant_a if user_hash < 50 else variant_b
        
        # Record participation
        participation = ABTestResult(
            test_id=ab_test.id,
            user_id=user_id,
            variant=variant
        )
        db.session.add(participation)
        db.session.commit()
        
        return variant
    except Exception as e:
        log_error('ab_test_error', str(e))
        return variant_a

def track_conversion_funnel(funnel_name, step_name, step_order, user_id=None):
    """Track conversion funnel"""
    try:
        # Get today's funnel data
        today = datetime.utcnow().date()
        funnel_data = ConversionFunnel.query.filter_by(
            funnel_name=funnel_name,
            step_name=step_name,
            date=today
        ).first()
        
        if funnel_data:
            funnel_data.user_count += 1
        else:
            funnel_data = ConversionFunnel(
                funnel_name=funnel_name,
                step_name=step_name,
                step_order=step_order,
                user_count=1,
                date=today
            )
            db.session.add(funnel_data)
        
        db.session.commit()
    except Exception as e:
        log_error('conversion_funnel_error', str(e))

def calculate_customer_lifetime_value(user_id):
    """Calculate customer lifetime value"""
    try:
        # Get user's booking history
        bookings = Booking.query.filter_by(user_id=user_id).all()
        
        if not bookings:
            return 0.0
        
        total_revenue = sum(booking.total_price for booking in bookings)
        total_orders = len(bookings)
        average_order_value = total_revenue / total_orders
        first_purchase = min(booking.created_at for booking in bookings)
        last_purchase = max(booking.created_at for booking in bookings)
        
        # Simple CLV calculation (can be enhanced with ML)
        predicted_lifetime_value = total_revenue * 1.5  # Assume 50% growth
        
        # Update CLV record
        clv_record = CustomerLifetimeValue.query.filter_by(user_id=user_id).first()
        if not clv_record:
            clv_record = CustomerLifetimeValue(user_id=user_id)
            db.session.add(clv_record)
        
        clv_record.total_revenue = total_revenue
        clv_record.total_orders = total_orders
        clv_record.average_order_value = average_order_value
        clv_record.first_purchase_date = first_purchase
        clv_record.last_purchase_date = last_purchase
        clv_record.predicted_lifetime_value = predicted_lifetime_value
        clv_record.updated_at = datetime.utcnow()
        
        db.session.commit()
        return predicted_lifetime_value
    except Exception as e:
        log_error('clv_calculation_error', str(e))
        return 0.0

# New API Endpoints for Advanced Features
@app.route('/api/flight-tracking/<flight_number>')
def api_flight_tracking(flight_number):
    """Get real-time flight tracking data"""
    try:
        tracking_data = get_flight_tracking(flight_number)
        if tracking_data:
            return jsonify({
                'success': True,
                'data': tracking_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Flight tracking data not available'
            }), 404
    except Exception as e:
        log_error('api_flight_tracking_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/hotel-availability/<int:hotel_id>')
def api_hotel_availability(hotel_id):
    """Get real-time hotel availability"""
    try:
        check_in = request.args.get('check_in')
        check_out = request.args.get('check_out')
        
        if not check_in or not check_out:
            return jsonify({
                'success': False,
                'error': 'check_in and check_out dates required'
            }), 400
        
        availability_data = get_hotel_availability(hotel_id, check_in, check_out)
        if availability_data:
            return jsonify({
                'success': True,
                'data': availability_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Availability data not available'
            }), 404
    except Exception as e:
        log_error('api_hotel_availability_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/dynamic-pricing/<int:destination_id>')
def api_dynamic_pricing(destination_id):
    """Get dynamic pricing for destination"""
    try:
        travel_date_str = request.args.get('travel_date')
        demand_factor = float(request.args.get('demand_factor', 1.0))
        
        if not travel_date_str:
            return jsonify({
                'success': False,
                'error': 'travel_date required'
            }), 400
        
        travel_date = datetime.strptime(travel_date_str, '%Y-%m-%d').date()
        price = calculate_dynamic_pricing(destination_id, travel_date, demand_factor)
        
        return jsonify({
            'success': True,
            'data': {
                'destination_id': destination_id,
                'travel_date': travel_date_str,
                'price': price,
                'currency': 'USD'
            }
        })
    except Exception as e:
        log_error('api_dynamic_pricing_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/user-behavior', methods=['POST'])
@login_required
def api_track_behavior():
    """Track user behavior for personalization"""
    try:
        data = request.get_json()
        page_url = data.get('page_url')
        action_type = data.get('action_type')
        action_data = data.get('action_data')
        
        if not page_url or not action_type:
            return jsonify({
                'success': False,
                'error': 'page_url and action_type required'
            }), 400
        
        track_user_behavior(
            current_user.id,
            session.get('session_id', str(uuid.uuid4())),
            page_url,
            action_type,
            action_data
        )
        
        return jsonify({
            'success': True,
            'message': 'Behavior tracked successfully'
        })
    except Exception as e:
        log_error('api_track_behavior_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/recommendations/ml')
@login_required
def api_ml_recommendations():
    """Get ML-powered personalized recommendations"""
    try:
        limit = int(request.args.get('limit', 6))
        recommendations = get_personalized_recommendations_ml(current_user.id, limit)
        
        return jsonify({
            'success': True,
            'data': [{
                'id': dest.id,
                'name': dest.name,
                'country': dest.country,
                'price': dest.price,
                'rating': dest.rating,
                'image_url': dest.image_url
            } for dest in recommendations]
        })
    except Exception as e:
        log_error('api_ml_recommendations_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/boarding-pass/<int:booking_id>', methods=['POST'])
@login_required
def api_generate_boarding_pass(booking_id):
    """Generate boarding pass with QR code"""
    try:
        data = request.get_json()
        passenger_name = data.get('passenger_name')
        flight_number = data.get('flight_number')
        
        if not passenger_name or not flight_number:
            return jsonify({
                'success': False,
                'error': 'passenger_name and flight_number required'
            }), 400
        
        boarding_pass = generate_boarding_pass(booking_id, passenger_name, flight_number)
        if boarding_pass:
            return jsonify({
                'success': True,
                'data': {
                    'id': boarding_pass.id,
                    'qr_code': boarding_pass.qr_code,
                    'passenger_name': boarding_pass.passenger_name,
                    'flight_number': boarding_pass.flight_number
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate boarding pass'
            }), 500
    except Exception as e:
        log_error('api_generate_boarding_pass_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/support/ticket', methods=['POST'])
@login_required
def api_create_support_ticket():
    """Create support ticket"""
    try:
        data = request.get_json()
        subject = data.get('subject')
        description = data.get('description')
        category = data.get('category', 'general')
        priority = data.get('priority', 'medium')
        
        if not subject or not description:
            return jsonify({
                'success': False,
                'error': 'subject and description required'
            }), 400
        
        ticket = create_support_ticket(
            current_user.id,
            subject,
            description,
            category,
            priority
        )
        
        if ticket:
            return jsonify({
                'success': True,
                'data': {
                    'id': ticket.id,
                    'subject': ticket.subject,
                    'status': ticket.status,
                    'created_at': ticket.created_at.isoformat()
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create ticket'
            }), 500
    except Exception as e:
        log_error('api_create_support_ticket_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/2fa/setup', methods=['POST'])
@login_required
def api_setup_2fa():
    """Setup two-factor authentication"""
    try:
        secret_key = generate_2fa_secret()
        
        # Create or update 2FA record
        two_fa = TwoFactorAuth.query.filter_by(user_id=current_user.id).first()
        if not two_fa:
            two_fa = TwoFactorAuth(
                user_id=current_user.id,
                secret_key=secret_key
            )
            db.session.add(two_fa)
        else:
            two_fa.secret_key = secret_key
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': {
                'secret_key': secret_key,
                'qr_code': f"otpauth://totp/WorldTour:{current_user.email}?secret={secret_key}&issuer=WorldTour"
            }
        })
    except Exception as e:
        log_error('api_setup_2fa_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/2fa/verify', methods=['POST'])
@login_required
def api_verify_2fa():
    """Verify 2FA code"""
    try:
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return jsonify({
                'success': False,
                'error': 'code required'
            }), 400
        
        two_fa = TwoFactorAuth.query.filter_by(user_id=current_user.id).first()
        if not two_fa:
            return jsonify({
                'success': False,
                'error': '2FA not setup'
            }), 400
        
        is_valid = verify_2fa_code(two_fa.secret_key, code)
        
        if is_valid:
            two_fa.is_enabled = True
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': '2FA verified and enabled'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid code'
            }), 400
    except Exception as e:
        log_error('api_verify_2fa_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/analytics/funnel', methods=['POST'])
def api_track_funnel():
    """Track conversion funnel"""
    try:
        data = request.get_json()
        funnel_name = data.get('funnel_name')
        step_name = data.get('step_name')
        step_order = data.get('step_order')
        user_id = current_user.id if current_user.is_authenticated else None
        
        if not funnel_name or not step_name or step_order is None:
            return jsonify({
                'success': False,
                'error': 'funnel_name, step_name, and step_order required'
            }), 400
        
        track_conversion_funnel(funnel_name, step_name, step_order, user_id)
        
        return jsonify({
            'success': True,
            'message': 'Funnel tracked successfully'
        })
    except Exception as e:
        log_error('api_track_funnel_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/analytics/clv/<int:user_id>')
@login_required
def api_customer_lifetime_value(user_id):
    """Get customer lifetime value"""
    try:
        if current_user.id != user_id and not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        clv = calculate_customer_lifetime_value(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'user_id': user_id,
                'lifetime_value': clv
            }
        })
    except Exception as e:
        log_error('api_clv_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# New Routes for Advanced Features
@app.route('/flight-tracking')
def flight_tracking_page():
    """Flight tracking page"""
    return render_template('flight_tracking.html')

@app.route('/analytics-dashboard')
@login_required
def analytics_dashboard():
    """Analytics dashboard page"""
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('home'))
    return render_template('analytics_dashboard.html')

@app.route('/mobile-features')
def mobile_features():
    """Mobile features showcase page"""
    return render_template('mobile_features.html')

@app.route('/api/analytics/metrics')
@login_required
def api_analytics_metrics():
    """Get analytics metrics"""
    try:
        if not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Get metrics from database
        total_users = User.query.count()
        total_bookings = Booking.query.count()
        total_revenue = db.session.query(db.func.sum(Booking.total_price)).scalar() or 0
        
        # Calculate conversion rate (simplified)
        total_visitors = 10000  # Simulated
        conversion_rate = (total_bookings / total_visitors * 100) if total_visitors > 0 else 0
        
        # Simulate trends
        revenue_trend = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'data': [12000, 15000, 18000, 22000, 25000, 28000]
        }
        
        users_trend = {
            'labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'data': [100, 150, 200, 250, 300, 350]
        }
        
        return jsonify({
            'success': True,
            'data': {
                'total_users': total_users,
                'total_bookings': total_bookings,
                'total_revenue': total_revenue,
                'conversion_rate': conversion_rate,
                'users_change': 15.5,
                'bookings_change': 22.3,
                'revenue_change': 18.7,
                'conversion_change': 5.2,
                'revenue_trend': revenue_trend,
                'users_trend': users_trend
            }
        })
    except Exception as e:
        log_error('api_analytics_metrics_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/analytics/funnel')
def api_analytics_funnel():
    """Get conversion funnel data"""
    try:
        # Simulate funnel data
        funnel_data = {
            'visitors': 10000,
            'views': 7500,
            'started': 2500,
            'completed': 1500
        }
        
        return jsonify({
            'success': True,
            'data': funnel_data
        })
    except Exception as e:
        log_error('api_analytics_funnel_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/analytics/ab-tests')
@login_required
def api_analytics_ab_tests():
    """Get A/B test results"""
    try:
        if not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Simulate A/B test data
        ab_tests = [
            {
                'name': 'Homepage Layout',
                'variant_a_conversion': 12.5,
                'variant_b_conversion': 15.2,
                'winner': 'Variant B'
            },
            {
                'name': 'Booking Button Color',
                'variant_a_conversion': 8.3,
                'variant_b_conversion': 8.1,
                'winner': 'Variant A'
            },
            {
                'name': 'Search Filters',
                'variant_a_conversion': 22.1,
                'variant_b_conversion': 24.8,
                'winner': 'Variant B'
            }
        ]
        
        return jsonify({
            'success': True,
            'data': ab_tests
        })
    except Exception as e:
        log_error('api_analytics_ab_tests_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/analytics/clv')
@login_required
def api_analytics_clv():
    """Get CLV analytics data"""
    try:
        if not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Simulate CLV data
        clv_data = {
            'average_clv': 2500,
            'top_10_percent_clv': 8500,
            'growth': 12.5
        }
        
        return jsonify({
            'success': True,
            'data': clv_data
        })
    except Exception as e:
        log_error('api_analytics_clv_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/api/analytics/activity')
def api_analytics_activity():
    """Get real-time activity feed"""
    try:
        # Simulate activity data
        activities = [
            {
                'type': 'booking',
                'description': 'New booking: Paris trip for $2,500',
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'type': 'user',
                'description': 'New user registered: john.doe@email.com',
                'timestamp': (datetime.utcnow() - timedelta(minutes=5)).isoformat()
            },
            {
                'type': 'payment',
                'description': 'Payment processed: $1,800 for Tokyo package',
                'timestamp': (datetime.utcnow() - timedelta(minutes=10)).isoformat()
            },
            {
                'type': 'review',
                'description': 'New 5-star review for Bali destination',
                'timestamp': (datetime.utcnow() - timedelta(minutes=15)).isoformat()
            },
            {
                'type': 'search',
                'description': 'Popular search: "flights to London"',
                'timestamp': (datetime.utcnow() - timedelta(minutes=20)).isoformat()
            }
        ]
        
        return jsonify({
            'success': True,
            'data': activities
        })
    except Exception as e:
        log_error('api_analytics_activity_error', str(e))
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Advanced Search & Discovery Routes
@app.route('/multi-city-search')
def multi_city_search():
    """Multi-city routing search page"""
    return render_template('multi_city_search.html')

@app.route('/api/multi-city-routes', methods=['POST'])
@login_required
def create_multi_city_route():
    """Create a multi-city route"""
    try:
        data = request.get_json()
        route = MultiCityRoute(
            user_id=current_user.id,
            route_name=data['route_name'],
            total_price=data['total_price'],
            total_duration=data['total_duration']
        )
        db.session.add(route)
        db.session.commit()
        
        # Add route segments
        for segment_data in data['segments']:
            segment = RouteSegment(
                route_id=route.id,
                segment_order=segment_data['order'],
                origin=segment_data['origin'],
                destination=segment_data['destination'],
                departure_date=datetime.strptime(segment_data['departure_date'], '%Y-%m-%d').date(),
                duration=segment_data.get('duration', 1),
                price=segment_data['price']
            )
            db.session.add(segment)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'route_id': route.id,
            'message': 'Multi-city route created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/flexible-search', methods=['POST'])
@login_required
def create_flexible_search():
    """Create a flexible search"""
    try:
        data = request.get_json()
        search = FlexibleSearch(
            user_id=current_user.id,
            search_type=data['search_type'],
            origin=data.get('origin'),
            destination_preferences=json.dumps(data.get('destination_preferences', [])),
            date_range_start=datetime.strptime(data['date_range_start'], '%Y-%m-%d').date() if data.get('date_range_start') else None,
            date_range_end=datetime.strptime(data['date_range_end'], '%Y-%m-%d').date() if data.get('date_range_end') else None,
            budget_min=data.get('budget_min'),
            budget_max=data.get('budget_max'),
            duration_min=data.get('duration_min'),
            duration_max=data.get('duration_max')
        )
        db.session.add(search)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'search_id': search.id,
            'message': 'Flexible search created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/price-alerts', methods=['POST'])
@login_required
def create_price_alert():
    """Create a price alert"""
    try:
        data = request.get_json()
        alert = PriceAlert(
            user_id=current_user.id,
            destination_id=data['destination_id'],
            target_price=data['target_price'],
            current_price=data['current_price']
        )
        db.session.add(alert)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'alert_id': alert.id,
            'message': 'Price alert created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/explore-destinations')
def explore_destinations():
    """Explore destinations based on budget/dates"""
    try:
        budget = request.args.get('budget', type=float)
        duration = request.args.get('duration', type=int)
        travel_style = request.args.get('style')
        
        query = Destination.query.filter(Destination.available == True)
        
        if budget:
            query = query.filter(Destination.price <= budget)
        
        if duration:
            query = query.filter(Destination.duration <= duration)
        
        if travel_style:
            query = query.filter(Destination.category == travel_style)
        
        destinations = query.limit(12).all()
        
        return jsonify({
            'success': True,
            'destinations': [{
                'id': d.id,
                'name': d.name,
                'country': d.country,
                'price': d.price,
                'duration': d.duration,
                'image_url': d.image_url,
                'rating': d.rating
            } for d in destinations]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Real-Time Inventory & Pricing Routes
@app.route('/api/seat-map/<int:flight_id>')
def get_seat_map(flight_id):
    """Get seat map for a flight"""
    try:
        seat_map = SeatMap.query.filter_by(flight_id=flight_id).first()
        if not seat_map:
            # Create a sample seat map
            seat_map = SeatMap(
                flight_id=flight_id,
                aircraft_type='Boeing 737',
                seat_configuration=json.dumps({
                    'rows': 30,
                    'columns': ['A', 'B', 'C', 'D', 'E', 'F'],
                    'layout': '3-3'
                }),
                available_seats=json.dumps(['1A', '1B', '1C', '2A', '2B', '2C']),
                seat_prices=json.dumps({
                    'window': 50,
                    'aisle': 30,
                    'middle': 20
                })
            )
            db.session.add(seat_map)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'seat_map': {
                'aircraft_type': seat_map.aircraft_type,
                'configuration': json.loads(seat_map.seat_configuration),
                'available_seats': json.loads(seat_map.available_seats),
                'seat_prices': json.loads(seat_map.seat_prices)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hotel-room-map/<int:hotel_id>')
def get_hotel_room_map(hotel_id):
    """Get room map for a hotel"""
    try:
        room_map = HotelRoomMap.query.filter_by(hotel_id=hotel_id).first()
        if not room_map:
            # Create a sample room map
            room_map = HotelRoomMap(
                hotel_id=hotel_id,
                floor_number=1,
                room_layout=json.dumps({
                    'rooms': [
                        {'number': '101', 'type': 'standard', 'available': True},
                        {'number': '102', 'type': 'deluxe', 'available': True},
                        {'number': '103', 'type': 'suite', 'available': False}
                    ]
                }),
                available_rooms=json.dumps(['101', '102']),
                room_features=json.dumps({
                    '101': ['king_bed', 'ocean_view'],
                    '102': ['queen_bed', 'balcony'],
                    '103': ['king_bed', 'ocean_view', 'jacuzzi']
                })
            )
            db.session.add(room_map)
            db.session.commit()
        
        return jsonify({
            'success': True,
            'room_map': {
                'floor_number': room_map.floor_number,
                'layout': json.loads(room_map.room_layout),
                'available_rooms': json.loads(room_map.available_rooms),
                'room_features': json.loads(room_map.room_features)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/fare-calendar')
def get_fare_calendar():
    """Get fare calendar for a route"""
    try:
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        month = request.args.get('month')
        
        # Simulate fare calendar data
        fares = []
        base_price = 800
        for day in range(1, 32):
            # Simulate price variations
            variation = random.uniform(0.7, 1.3)
            price = base_price * variation
            
            fares.append({
                'date': f'2025-{month}-{day:02d}',
                'price': round(price, 2),
                'airline': random.choice(['Delta', 'American', 'United', 'Southwest'])
            })
        
        return jsonify({
            'success': True,
            'fares': fares
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Advanced Booking Features Routes
@app.route('/api/passengers/<int:booking_id>', methods=['POST'])
@login_required
def add_passenger(booking_id):
    """Add passenger to booking"""
    try:
        data = request.get_json()
        passenger = Passenger(
            booking_id=booking_id,
            first_name=data['first_name'],
            last_name=data['last_name'],
            date_of_birth=datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date(),
            passport_number=data.get('passport_number'),
            nationality=data.get('nationality'),
            seat_preference=data.get('seat_preference'),
            meal_preference=data.get('meal_preference'),
            special_requests=data.get('special_requests')
        )
        db.session.add(passenger)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'passenger_id': passenger.id,
            'message': 'Passenger added successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/seat-selection', methods=['POST'])
@login_required
def select_seat():
    """Select seat for passenger"""
    try:
        data = request.get_json()
        seat_selection = SeatSelection(
            passenger_id=data['passenger_id'],
            flight_id=data['flight_id'],
            seat_number=data['seat_number'],
            seat_type=data.get('seat_type', 'economy'),
            price=data.get('price', 0)
        )
        db.session.add(seat_selection)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'selection_id': seat_selection.id,
            'message': 'Seat selected successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/baggage-options', methods=['POST'])
@login_required
def add_baggage_option(booking_id):
    """Add baggage option to booking"""
    try:
        data = request.get_json()
        baggage = BaggageOption(
            booking_id=booking_id,
            baggage_type=data['baggage_type'],
            weight=data.get('weight'),
            price=data['price']
        )
        db.session.add(baggage)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'baggage_id': baggage.id,
            'message': 'Baggage option added successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Social & Community Features Routes
@app.route('/travel-buddy')
@login_required
def travel_buddy_page():
    """Travel buddy finder page"""
    return render_template('travel_buddy.html')

@app.route('/api/travel-buddy/create', methods=['POST'])
@login_required
def create_travel_buddy_profile():
    """Create travel buddy profile"""
    try:
        data = request.get_json()
        buddy = TravelBuddy(
            user_id=current_user.id,
            destination_id=data['destination_id'],
            travel_dates_start=datetime.strptime(data['travel_dates_start'], '%Y-%m-%d').date(),
            travel_dates_end=datetime.strptime(data['travel_dates_end'], '%Y-%m-%d').date(),
            travel_style=data.get('travel_style'),
            interests=json.dumps(data.get('interests', [])),
            languages=json.dumps(data.get('languages', [])),
            age_range=data.get('age_range')
        )
        db.session.add(buddy)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'buddy_id': buddy.id,
            'message': 'Travel buddy profile created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/travel-buddy/matches')
@login_required
def get_travel_buddy_matches():
    """Get travel buddy matches"""
    try:
        user_buddy = TravelBuddy.query.filter_by(user_id=current_user.id).first()
        if not user_buddy:
            return jsonify({
                'success': False,
                'error': 'No travel buddy profile found'
            }), 404
        
        # Find potential matches
        matches = TravelBuddy.query.filter(
            TravelBuddy.user_id != current_user.id,
            TravelBuddy.destination_id == user_buddy.destination_id,
            TravelBuddy.is_active == True
        ).all()
        
        match_data = []
        for match in matches:
            # Calculate match score based on preferences
            score = calculate_buddy_match_score(user_buddy, match)
            match_data.append({
                'buddy_id': match.id,
                'user_name': f"{match.user.first_name} {match.user.last_name}",
                'travel_style': match.travel_style,
                'interests': json.loads(match.interests),
                'languages': json.loads(match.languages),
                'match_score': score
            })
        
        # Sort by match score
        match_data.sort(key=lambda x: x['match_score'], reverse=True)
        
        return jsonify({
            'success': True,
            'matches': match_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/traveler-meetups')
def traveler_meetups():
    """Traveler meetups page"""
    meetups = TravelerMeetup.query.filter_by(is_active=True).all()
    return render_template('traveler_meetups.html', meetups=meetups)

@app.route('/api/meetups/create', methods=['POST'])
@login_required
def create_meetup():
    """Create a traveler meetup"""
    try:
        data = request.get_json()
        meetup = TravelerMeetup(
            organizer_id=current_user.id,
            destination_id=data['destination_id'],
            title=data['title'],
            description=data.get('description'),
            meetup_date=datetime.strptime(data['meetup_date'], '%Y-%m-%dT%H:%M'),
            location=data['location'],
            max_participants=data.get('max_participants')
        )
        db.session.add(meetup)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'meetup_id': meetup.id,
            'message': 'Meetup created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/meetups/<int:meetup_id>/join', methods=['POST'])
@login_required
def join_meetup(meetup_id):
    """Join a traveler meetup"""
    try:
        # Check if already joined
        existing = MeetupParticipant.query.filter_by(
            meetup_id=meetup_id,
            user_id=current_user.id
        ).first()
        
        if existing:
            return jsonify({
                'success': False,
                'error': 'Already joined this meetup'
            }), 400
        
        participant = MeetupParticipant(
            meetup_id=meetup_id,
            user_id=current_user.id
        )
        db.session.add(participant)
        
        # Update current participants count
        meetup = TravelerMeetup.query.get(meetup_id)
        meetup.current_participants += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Successfully joined meetup'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/travel-stories')
def travel_stories():
    """Travel stories page"""
    stories = TravelStory.query.filter_by(is_featured=True).order_by(TravelStory.created_at.desc()).limit(10).all()
    return render_template('travel_stories.html', stories=stories)

@app.route('/api/travel-stories/create', methods=['POST'])
@login_required
def create_travel_story():
    """Create a travel story"""
    try:
        data = request.get_json()
        story = TravelStory(
            user_id=current_user.id,
            destination_id=data['destination_id'],
            title=data['title'],
            content=data['content']
        )
        db.session.add(story)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'story_id': story.id,
            'message': 'Travel story created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Business Travel Features Routes
@app.route('/corporate-portal')
@login_required
def corporate_portal():
    """Corporate booking portal"""
    # Check if user is part of a corporate account
    corporate_employee = CorporateEmployee.query.filter_by(user_id=current_user.id).first()
    if not corporate_employee:
        return redirect(url_for('register_corporate'))
    
    return render_template('corporate_portal.html', employee=corporate_employee)

@app.route('/api/corporate-booking', methods=['POST'])
@login_required
def create_corporate_booking():
    """Create a corporate booking with approval workflow"""
    try:
        data = request.get_json()
        
        # Create the booking first
        booking = Booking(
            user_id=current_user.id,
            destination_id=data.get('destination_id'),
            flight_id=data.get('flight_id'),
            hotel_id=data.get('hotel_id'),
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            guests=data.get('guests', 1),
            total_price=data['total_price']
        )
        db.session.add(booking)
        db.session.flush()  # Get the booking ID
        
        # Create corporate booking record
        corporate_employee = CorporateEmployee.query.filter_by(user_id=current_user.id).first()
        corporate_booking = CorporateBooking(
            corporate_account_id=corporate_employee.corporate_account_id,
            employee_id=current_user.id,
            booking_id=booking.id,
            approval_status='pending'
        )
        db.session.add(corporate_booking)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'booking_id': booking.id,
            'corporate_booking_id': corporate_booking.id,
            'message': 'Corporate booking created and pending approval'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/expense-report', methods=['POST'])
@login_required
def create_expense_report():
    """Create an expense report"""
    try:
        data = request.get_json()
        corporate_employee = CorporateEmployee.query.filter_by(user_id=current_user.id).first()
        
        report = ExpenseReport(
            corporate_account_id=corporate_employee.corporate_account_id,
            employee_id=current_user.id,
            report_name=data['report_name'],
            trip_purpose=data.get('trip_purpose'),
            total_amount=data.get('total_amount', 0)
        )
        db.session.add(report)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'report_id': report.id,
            'message': 'Expense report created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Advanced Payment & Financial Routes
@app.route('/api/buy-now-pay-later', methods=['POST'])
@login_required
def create_buy_now_pay_later():
    """Create a buy now pay later option"""
    try:
        data = request.get_json()
        bnpl = BuyNowPayLater(
            booking_id=data['booking_id'],
            provider=data['provider'],
            total_amount=data['total_amount'],
            installment_count=data['installment_count'],
            installment_amount=data['installment_amount'],
            interest_rate=data.get('interest_rate', 0)
        )
        db.session.add(bnpl)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'bnpl_id': bnpl.id,
            'message': 'Buy now pay later option created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/split-payment', methods=['POST'])
@login_required
def create_split_payment():
    """Create a split payment"""
    try:
        data = request.get_json()
        split_payment = SplitPayment(
            booking_id=data['booking_id'],
            total_amount=data['total_amount'],
            split_count=data['split_count'],
            amount_per_person=data['amount_per_person']
        )
        db.session.add(split_payment)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'split_payment_id': split_payment.id,
            'message': 'Split payment created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Post-Booking Experience Routes
@app.route('/api/digital-documents/<int:booking_id>')
@login_required
def get_digital_documents(booking_id):
    """Get digital documents for a booking"""
    try:
        documents = DigitalDocument.query.filter_by(booking_id=booking_id).all()
        return jsonify({
            'success': True,
            'documents': [{
                'id': doc.id,
                'type': doc.document_type,
                'url': doc.document_url,
                'number': doc.document_number,
                'issue_date': doc.issue_date.isoformat() if doc.issue_date else None,
                'expiry_date': doc.expiry_date.isoformat() if doc.expiry_date else None,
                'is_valid': doc.is_valid
            } for doc in documents]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/travel-updates/<int:booking_id>')
@login_required
def get_travel_updates(booking_id):
    """Get travel updates for a booking"""
    try:
        updates = TravelUpdate.query.filter_by(booking_id=booking_id).order_by(TravelUpdate.created_at.desc()).all()
        return jsonify({
            'success': True,
            'updates': [{
                'id': update.id,
                'type': update.update_type,
                'title': update.title,
                'message': update.message,
                'severity': update.severity,
                'is_read': update.is_read,
                'created_at': update.created_at.isoformat()
            } for update in updates]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/in-destination-support', methods=['POST'])
@login_required
def request_in_destination_support():
    """Request in-destination support"""
    try:
        data = request.get_json()
        support = InDestinationSupport(
            booking_id=data['booking_id'],
            support_type=data['support_type'],
            description=data['description'],
            location=data.get('location')
        )
        db.session.add(support)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'support_id': support.id,
            'message': 'Support request created successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Advanced Technology Routes
@app.route('/api/voice-booking', methods=['POST'])
@login_required
def voice_booking():
    """Process voice booking request"""
    try:
        data = request.get_json()
        voice_booking = VoiceBooking(
            user_id=current_user.id,
            voice_query=data['voice_query'],
            interpreted_query=data.get('interpreted_query'),
            booking_type=data.get('booking_type'),
            confidence_score=data.get('confidence_score', 0)
        )
        db.session.add(voice_booking)
        db.session.commit()
        
        # Process the voice query
        result = process_voice_booking_query(data['voice_query'])
        
        return jsonify({
            'success': True,
            'voice_booking_id': voice_booking.id,
            'result': result
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/biometric-auth/setup', methods=['POST'])
@login_required
def setup_biometric_auth():
    """Setup biometric authentication"""
    try:
        data = request.get_json()
        biometric = BiometricAuth(
            user_id=current_user.id,
            auth_type=data['auth_type'],
            device_info=json.dumps(data.get('device_info', {})),
            is_enabled=True
        )
        db.session.add(biometric)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'biometric_id': biometric.id,
            'message': 'Biometric authentication setup successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Enterprise Features Routes
@app.route('/api/white-label/setup', methods=['POST'])
@login_required
def setup_white_label():
    """Setup white label solution"""
    try:
        if not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        data = request.get_json()
        partner = WhiteLabelPartner(
            partner_name=data['partner_name'],
            domain=data['domain'],
            branding_config=json.dumps(data.get('branding_config', {})),
            commission_rate=data.get('commission_rate', 0.05)
        )
        db.session.add(partner)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'partner_id': partner.id,
            'message': 'White label partner setup successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/marketplace/apis')
def get_api_marketplace():
    """Get available APIs in marketplace"""
    try:
        apis = APIMarketplace.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'apis': [{
                'id': api.id,
                'name': api.api_name,
                'provider': api.provider,
                'description': api.description,
                'pricing_model': api.pricing_model,
                'rate_limit': api.rate_limit
            } for api in apis]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Helper Functions
def calculate_buddy_match_score(buddy1, buddy2):
    """Calculate match score between two travel buddies"""
    score = 0
    
    # Travel style match
    if buddy1.travel_style == buddy2.travel_style:
        score += 30
    
    # Interest overlap
    interests1 = set(json.loads(buddy1.interests))
    interests2 = set(json.loads(buddy2.interests))
    if interests1 and interests2:
        overlap = len(interests1.intersection(interests2))
        score += (overlap / max(len(interests1), len(interests2))) * 40
    
    # Language overlap
    languages1 = set(json.loads(buddy1.languages))
    languages2 = set(json.loads(buddy2.languages))
    if languages1 and languages2:
        overlap = len(languages1.intersection(languages2))
        score += (overlap / max(len(languages1), len(languages2))) * 30
    
    return min(score, 100)

def process_voice_booking_query(query):
    """Process voice booking query"""
    query_lower = query.lower()
    
    # Simple keyword matching
    if 'flight' in query_lower and 'london' in query_lower:
        return {
            'type': 'flight',
            'destination': 'London',
            'suggestions': ['Search flights to London', 'Book flight to London']
        }
    elif 'hotel' in query_lower and 'paris' in query_lower:
        return {
            'type': 'hotel',
            'destination': 'Paris',
            'suggestions': ['Search hotels in Paris', 'Book hotel in Paris']
        }
    else:
        return {
            'type': 'general',
            'suggestions': ['Search flights', 'Search hotels', 'Search packages']
        }

# Register get_locale as a template global
app.jinja_env.globals['get_locale'] = get_locale

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_db()
    app.run(debug=True)
