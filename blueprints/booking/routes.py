from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from db import db
from new_models import Destination, Hotel, Flight, Booking, Review, WishlistItem
from datetime import datetime

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/destinations')
def destinations():
    all_destinations = Destination.query.filter_by(available=True).all()
    if request.is_json or request.args.get('format') == 'json':
        return jsonify([{
            'id': d.id,
            'name': d.name,
            'country': d.country,
            'image_url': d.image_url,
            'price': d.price,
            'rating': 5,
            'category': d.category
        } for d in all_destinations])
    return render_template('travel.html', destinations=all_destinations)

@booking_bp.route('/hotels')
def hotels():
    all_hotels = Hotel.query.all()
    if request.is_json or request.args.get('format') == 'json':
        return jsonify([{
            'id': h.id,
            'name': h.name,
            'location': h.location,
            'price': h.price,
            'rating': h.rating,
            'image_url': h.image_url,
            'description': h.description
        } for h in all_hotels])
    return render_template('hotels.html', hotels=all_hotels)

@booking_bp.route('/flights')
def flights():
    all_flights = Flight.query.all()
    if request.is_json or request.args.get('format') == 'json':
        return jsonify([{
            'id': f.id,
            'airline': f.airline,
            'origin': f.origin,
            'destination': f.destination,
            'price': f.price,
            'departure': f.departure_time.strftime('%I:%M %p') if f.departure_time else '10:00 AM',
            'duration': f.duration
        } for f in all_flights])
    return render_template('flights.html', flights=all_flights)
