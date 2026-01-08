from db import db
from datetime import datetime
from flask_login import UserMixin
import json

# Advanced Search & Discovery Models
class MultiCityRoute(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    route_name = db.Column(db.String(100), nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    total_duration = db.Column(db.Integer)  # days
    is_saved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='multi_city_routes')
    segments = db.relationship('RouteSegment', backref='route', lazy=True, cascade='all, delete-orphan')

class RouteSegment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.Integer, db.ForeignKey('multi_city_route.id'), nullable=False)
    segment_order = db.Column(db.Integer, nullable=False)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'))
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'))
    duration = db.Column(db.Integer)  # days at this destination
    price = db.Column(db.Float, nullable=False)

class FlexibleSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    search_type = db.Column(db.String(50))  # flexible_dates, flexible_destination, budget_explore
    origin = db.Column(db.String(100))
    destination_preferences = db.Column(db.Text)  # JSON array
    date_range_start = db.Column(db.Date)
    date_range_end = db.Column(db.Date)
    budget_min = db.Column(db.Float)
    budget_max = db.Column(db.Float)
    duration_min = db.Column(db.Integer)
    duration_max = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='flexible_searches')

class SearchHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    search_query = db.Column(db.Text, nullable=False)
    search_type = db.Column(db.String(50))  # flight, hotel, package, destination
    results_count = db.Column(db.Integer, default=0)
    clicked_result = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    bookings = db.relationship('Booking', backref='user', lazy=True)

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer)
    image_url = db.Column(db.String(500))
    category = db.Column(db.String(50))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    climate = db.Column(db.String(50))
    best_time_to_visit = db.Column(db.String(50))
    available = db.Column(db.Boolean, default=True)
    bookings = db.relationship('Booking', backref='destination', lazy=True)

class Hotel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    price = db.Column(db.Float)
    rating = db.Column(db.Float)
    image_url = db.Column(db.String(500))
    description = db.Column(db.Text)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'))

class Flight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    airline = db.Column(db.String(100))
    origin = db.Column(db.String(50))
    destination = db.Column(db.String(50))
    price = db.Column(db.Float)
    departure_time = db.Column(db.DateTime)
    duration = db.Column(db.String(20))
    flight_number = db.Column(db.String(20))

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'))
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='confirmed')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WishlistItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AITravelAssistant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    conversation_id = db.Column(db.String(100), default='default')
    message_type = db.Column(db.String(20)) # 'user' or 'assistant'
    message_content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_type = db.Column(db.String(50))
    event_data = db.Column(db.Text) # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
