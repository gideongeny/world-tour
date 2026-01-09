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
            'rating': d.rating or 4.5,
            'category': d.category,
            'quote': d.quote,
            'latitude': d.latitude,
            'longitude': d.longitude
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
@booking_bp.route('/external/hotels/search')
def external_hotel_search():
    from services.redirect_service import redirect_service
    dest = request.args.get('q', 'Paris')
    checkin = request.args.get('checkin') # YYYY-MM-DD
    checkout = request.args.get('checkout') # YYYY-MM-DD
    
    url = redirect_service.get_booking_url(dest, checkin, checkout)
    return jsonify({'url': url})

@booking_bp.route('/live/hotels/search')
def live_hotel_search():
    from services.liteapi_service import liteapi_service
    dest = request.args.get('q', 'Paris')
    guests = request.args.get('guests', 2)
    checkin = request.args.get('checkin')
    checkout = request.args.get('checkout')
    
    hotels = liteapi_service.search_hotels(dest, guests, checkin, checkout)
    return jsonify(hotels)

@booking_bp.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    from services.stripe_service import stripe_service
    data = request.json
    item_name = data.get('name', 'Travel Booking')
    amount = data.get('price', 0)
    
    # In a real app, success/cancel URLs would be your production domain
    host = request.host_url.rstrip('/')
    success_url = f"{host}/checkout?success=true"
    cancel_url = f"{host}/checkout?cancel=true"
    
    url, session_id = stripe_service.create_checkout_session(item_name, amount, success_url, cancel_url)
    
    if url:
        return jsonify({'url': url, 'sessionId': session_id})
    return jsonify({'error': 'Failed to create checkout session'}), 500
@booking_bp.route('/external/flights/search')
def external_flight_search():
    from services.redirect_service import redirect_service
    origin = request.args.get('origin', 'NYC')
    dest = request.args.get('dest', 'PAR')
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    url = redirect_service.get_google_flights_url(origin, dest, date)
    return jsonify({'url': url})
