from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from db import db
from new_models import Destination, Hotel, Flight, PackageDeal, Booking, Review, WishlistItem
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
            'rating': d.rating,
            'category': d.category
        } for d in all_destinations])
    return render_template('travel.html', destinations=all_destinations)

from services.weather import weather_service

@booking_bp.route('/destination/<int:destination_id>')
def destination_detail(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    reviews = Review.query.filter_by(destination_id=destination_id).all()
    
    # Get real-time weather for the destination
    weather = weather_service.get_weather(destination.name if ',' not in destination.name else destination.name.split(',')[0])
    
    return render_template('destination_detail.html', 
                         destination=destination, 
                         reviews=reviews,
                         weather=weather)

@booking_bp.route('/book/<int:destination_id>', methods=['POST'])
@login_required
def book_destination(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    new_booking = Booking(
        user_id=current_user.id,
        destination_id=destination_id,
        total_price=destination.price,
        status='confirmed'
    )
    db.session.add(new_booking)
    db.session.commit()
    
    if request.is_json:
        return jsonify({'success': True, 'booking_id': new_booking.id})
    flash('Booking confirmed!', 'success')
    return redirect(url_for('booking.destinations'))

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

@booking_bp.route('/packages')
def packages():
    all_packages = PackageDeal.query.all()
    return render_template('packages.html', packages=all_packages)

# Add more detailed booking routes as needed
