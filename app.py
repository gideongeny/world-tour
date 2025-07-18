from flask import Flask, render_template, request, redirect, jsonify, url_for, flash, session, make_response, g
from werkzeug.utils import secure_filename
from db import db
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
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

# Database configuration for production
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///world_tour.db')
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
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'your-email@gmail.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', 'your-app-password')

# Import new models
from new_models import *

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
# To enable Redis on Render, set up a Redis instance and update the config below
redis_client = None  # Example: redis.Redis(host=os.environ.get('REDIS_HOST'), port=6379, password=os.environ.get('REDIS_PASSWORD'))

# Celery configuration (disabled for development)
# To enable Celery on Render, set up a Redis instance and configure the broker URL
celery_app = None  # Example: Celery(app.name, broker=os.environ.get('REDIS_URL'))

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
    # print(f"Current language: {current_lang}")  # Debug
    return dict(languages=app.config['LANGUAGES'], current_language=current_lang)

@app.context_processor
def inject_currencies():
    current_curr = session.get('currency', app.config['DEFAULT_CURRENCY'])
    # print(f"Current currency: {current_curr}")  # Debug
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
        },
        'ja': {
            'home': 'ホーム',
            'destinations': '目的地',
            'flights': 'フライト',
            'hotels': 'ホテル',
            'packages': 'パッケージ',
            'blog': 'ブログ',
            'offers': 'オファー',
            'contact': 'お問い合わせ',
            'login': 'ログイン',
            'register': '登録',
            'profile': 'プロフィール',
            'logout': 'ログアウト',
            'search': '検索',
            'book_now': '今すぐ予約',
            'view_details': '詳細を見る',
            'price_from': 'から',
            'per_person': '1人あたり',
            'per_night': '1泊あたり',
            'welcome_message': 'ワールドツアーへようこそ',
            'discover_amazing': '素晴らしい目的地を発見',
            'explore_world': '私たちと一緒に世界を探検しましょう',
            'featured_destinations': '注目の目的地',
            'popular_destinations': '人気の目的地',
            'special_offers': '特別オファー',
            'newsletter_signup': 'ニュースレターに登録',
            'get_best_deals': 'お得な情報と旅行のヒントをゲット',
            'subscribe': '購読する',
            'email_placeholder': 'メールアドレスを入力',
            'footer_description': '世界中の素晴らしい旅行体験へのゲートウェイ。',
            'quick_links': 'クイックリンク',
            'support': 'サポート',
            'help_center': 'ヘルプセンター',
            'my_tickets': 'マイチケット',
            'contact_info': 'お問い合わせ',
            'all_rights_reserved': '全著作権所有。',
            'luxury_destinations': '高級目的地',
            'budget_destinations': '格安目的地',
            'adventure_destinations': '冒険の目的地',
            'all_destinations': 'すべての目的地',
            'travel_guides': '旅行ガイド',
            'interactive_maps': 'インタラクティブマップ',
            'flash_deals': 'フラッシュディール',
            'seasonal_offers': '季節限定オファー',
            'last_minute_deals': '直前割引',
            'all_special_offers': 'すべての特別オファー',
            'loyalty_rewards': 'ロイヤルティリワード',
            'group_discounts': 'グループ割引'
        },
        'zh': {
            'home': '首页',
            'destinations': '目的地',
            'flights': '航班',
            'hotels': '酒店',
            'packages': '套餐',
            'blog': '博客',
            'offers': '优惠',
            'contact': '联系我们',
            'login': '登录',
            'register': '注册',
            'profile': '个人资料',
            'logout': '登出',
            'search': '搜索',
            'book_now': '立即预订',
            'view_details': '查看详情',
            'price_from': '起',
            'per_person': '每人',
            'per_night': '每晚',
            'welcome_message': '欢迎来到世界之旅',
            'discover_amazing': '发现惊人的目的地',
            'explore_world': '与我们一起探索世界',
            'featured_destinations': '特色目的地',
            'popular_destinations': '热门目的地',
            'special_offers': '特别优惠',
            'newsletter_signup': '订阅我们的新闻',
            'get_best_deals': '获取最佳优惠和旅行建议',
            'subscribe': '订阅',
            'email_placeholder': '输入您的邮箱',
            'footer_description': '您通往世界各地精彩旅行体验的大门。',
            'quick_links': '快速链接',
            'support': '支持',
            'help_center': '帮助中心',
            'my_tickets': '我的票',
            'contact_info': '联系方式',
            'all_rights_reserved': '版权所有。',
            'luxury_destinations': '豪华目的地',
            'budget_destinations': '经济型目的地',
            'adventure_destinations': '冒险目的地',
            'all_destinations': '所有目的地',
            'travel_guides': '旅行指南',
            'interactive_maps': '互动地图',
            'flash_deals': '限时优惠',
            'seasonal_offers': '季节性优惠',
            'last_minute_deals': '最后时刻优惠',
            'all_special_offers': '所有特别优惠',
            'loyalty_rewards': '忠诚奖励',
            'group_discounts': '团体折扣'
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
    white_label_partner_id = db.Column(db.Integer, db.ForeignKey('white_label_partner.id'))
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
    
    # Get all available destinations with all images
    all_destinations = Destination.query.with_entities(
        Destination.id, Destination.name, Destination.country, 
        Destination.price, Destination.rating, Destination.image_url, Destination.description,
        Destination.category, Destination.duration, Destination.reviews_count
    ).filter_by(available=True).all()
    
    # Featured destinations (top rated)
    featured_destinations = sorted(all_destinations, key=lambda x: x.rating, reverse=True)[:6]
    
    # Latest destinations
    latest_destinations = sorted(all_destinations, key=lambda x: x.id, reverse=True)[:3]
    
    # Category destinations for the categories section
    category_destinations = {
        'luxury': [d for d in all_destinations if d.category == 'luxury'][:4],
        'budget': [d for d in all_destinations if d.category == 'budget'][:4],
        'adventure': [d for d in all_destinations if d.category == 'adventure'][:4],
        'beach': [d for d in all_destinations if d.category == 'beach'][:4],
        'cultural': [d for d in all_destinations if d.category == 'cultural'][:4]
    }
    
    # Popular destinations by reviews
    popular_destinations = sorted(all_destinations, key=lambda x: x.reviews_count, reverse=True)[:6]
    
    return render_template('index.html', 
                         featured_destinations=featured_destinations,
                         latest_destinations=latest_destinations,
                         personalized_destinations=personalized_destinations,
                         category_destinations=category_destinations,
                         popular_destinations=popular_destinations)

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

def init_db():
    db.create_all()
    # Add any initial data setup here

@app.route('/local-events')
def local_events():
    return render_template('local_events.html')

@app.route('/video-content')
def video_content():
    return render_template('video_content.html')

@app.route('/travel-insurance')
def travel_insurance():
    return render_template('travel_insurance.html')

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
