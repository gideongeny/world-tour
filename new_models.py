from db import db
from datetime import datetime
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
    user = db.relationship('User', backref='search_history')

class SavedSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    search_name = db.Column(db.String(100), nullable=False)
    search_criteria = db.Column(db.Text, nullable=False)  # JSON
    notification_enabled = db.Column(db.Boolean, default=True)
    last_searched = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='saved_searches')

# Real-Time Inventory & Pricing Models
class SeatMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    aircraft_type = db.Column(db.String(50), nullable=False)
    seat_configuration = db.Column(db.Text, nullable=False)  # JSON with seat layout
    available_seats = db.Column(db.Text)  # JSON with available seat numbers
    seat_prices = db.Column(db.Text)  # JSON with seat-specific pricing
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    flight = db.relationship('Flight', backref='seat_maps')

class HotelRoomMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    floor_number = db.Column(db.Integer, nullable=False)
    room_layout = db.Column(db.Text, nullable=False)  # JSON with room positions
    available_rooms = db.Column(db.Text)  # JSON with available room numbers
    room_features = db.Column(db.Text)  # JSON with room-specific features
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    hotel = db.relationship('Hotel', backref='room_maps')

class CompetitorPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    competitor_name = db.Column(db.String(100), nullable=False)
    competitor_price = db.Column(db.Float, nullable=False)
    our_price = db.Column(db.Float, nullable=False)
    price_difference = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    last_checked = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='competitor_prices')

class PricePrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    current_price = db.Column(db.Float, nullable=False)
    predicted_price = db.Column(db.Float, nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.Date, nullable=False)
    factors = db.Column(db.Text)  # JSON with prediction factors
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='price_predictions')

class FareCalendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    origin = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    departure_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date)
    price = db.Column(db.Float, nullable=False)
    airline = db.Column(db.String(100))
    flight_class = db.Column(db.String(20))  # economy, business, first
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# Advanced Booking Features Models
class Passenger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    passport_number = db.Column(db.String(50))
    nationality = db.Column(db.String(50))
    seat_preference = db.Column(db.String(20))  # window, aisle, middle
    meal_preference = db.Column(db.String(50))  # vegetarian, halal, kosher, etc.
    special_requests = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='passengers')

class SeatSelection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    passenger_id = db.Column(db.Integer, db.ForeignKey('passenger.id'), nullable=False)
    flight_id = db.Column(db.Integer, db.ForeignKey('flight.id'), nullable=False)
    seat_number = db.Column(db.String(10), nullable=False)
    seat_type = db.Column(db.String(20))  # economy, premium, business
    price = db.Column(db.Float, nullable=False)
    is_confirmed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    passenger = db.relationship('Passenger', backref='seat_selections')
    flight = db.relationship('Flight', backref='seat_selections')

class BaggageOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    baggage_type = db.Column(db.String(20))  # checked, carry_on, oversized
    weight = db.Column(db.Float)  # kg
    price = db.Column(db.Float, nullable=False)
    is_purchased = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='baggage_options')

class InsuranceComparison(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    provider_name = db.Column(db.String(100), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    coverage_details = db.Column(db.Text)  # JSON with coverage info
    price = db.Column(db.Float, nullable=False)
    is_selected = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='insurance_options')

class CarRental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    car_type = db.Column(db.String(50), nullable=False)
    pickup_location = db.Column(db.String(200), nullable=False)
    dropoff_location = db.Column(db.String(200), nullable=False)
    pickup_date = db.Column(db.DateTime, nullable=False)
    dropoff_date = db.Column(db.DateTime, nullable=False)
    price_per_day = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    insurance_included = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='car_rentals')

# Social & Community Features Models
class TravelBuddy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    travel_dates_start = db.Column(db.Date, nullable=False)
    travel_dates_end = db.Column(db.Date, nullable=False)
    travel_style = db.Column(db.String(50))  # luxury, budget, adventure, cultural
    interests = db.Column(db.Text)  # JSON array
    languages = db.Column(db.Text)  # JSON array
    age_range = db.Column(db.String(20))  # 18-25, 26-35, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='travel_buddy_profiles')
    destination = db.relationship('Destination', backref='travel_buddies')

class BuddyMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buddy1_id = db.Column(db.Integer, db.ForeignKey('travel_buddy.id'), nullable=False)
    buddy2_id = db.Column(db.Integer, db.ForeignKey('travel_buddy.id'), nullable=False)
    match_score = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, declined
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    buddy1 = db.relationship('TravelBuddy', foreign_keys=[buddy1_id], backref='matches_as_buddy1')
    buddy2 = db.relationship('TravelBuddy', foreign_keys=[buddy2_id], backref='matches_as_buddy2')

class TravelerMeetup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    organizer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    meetup_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    max_participants = db.Column(db.Integer)
    current_participants = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    organizer = db.relationship('User', backref='organized_meetups')
    destination = db.relationship('Destination', backref='meetups')
    participants = db.relationship('MeetupParticipant', backref='meetup', lazy=True, cascade='all, delete-orphan')

class MeetupParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    meetup_id = db.Column(db.Integer, db.ForeignKey('traveler_meetup.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='confirmed')  # confirmed, maybe, declined
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='meetup_participations')

class TravelStory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='travel_stories')
    destination = db.relationship('Destination', backref='travel_stories')
    photos = db.relationship('StoryPhoto', backref='story', lazy=True, cascade='all, delete-orphan')

class StoryPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey('travel_story.id'), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    caption = db.Column(db.String(200))
    location_tag = db.Column(db.String(200))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

class TravelerVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    verification_type = db.Column(db.String(50))  # email, phone, id_document, social_media
    verification_status = db.Column(db.String(20), default='pending')  # pending, verified, rejected
    verification_score = db.Column(db.Float, default=0.0)
    verified_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='verifications')

# Advanced Personalization Models
class AITravelAssistant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    conversation_id = db.Column(db.String(100), nullable=False)
    message_type = db.Column(db.String(20))  # user, assistant
    message_content = db.Column(db.Text, nullable=False)
    intent_detected = db.Column(db.String(100))
    confidence_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='ai_conversations')

class SocialMediaIntegration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(50))  # facebook, instagram, twitter, linkedin
    access_token = db.Column(db.Text)
    profile_data = db.Column(db.Text)  # JSON with profile info
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='social_integrations')

class TravelStyle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    style_type = db.Column(db.String(50))  # luxury, budget, adventure, cultural, family
    confidence_score = db.Column(db.Float, default=0.0)
    source = db.Column(db.String(50))  # explicit, inferred, ml
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='travel_styles')

class SeasonalRecommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    season = db.Column(db.String(20))  # spring, summer, autumn, winter
    recommendation_reason = db.Column(db.Text)
    weather_info = db.Column(db.Text)  # JSON with weather data
    activities = db.Column(db.Text)  # JSON with seasonal activities
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='seasonal_recommendations')

class AccessibilityFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    feature_type = db.Column(db.String(50))  # wheelchair, hearing, vision, mobility
    description = db.Column(db.Text)
    availability = db.Column(db.String(20))  # available, limited, not_available
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='accessibility_features')

class FamilyFriendlyFeature(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)
    feature_type = db.Column(db.String(50))  # playground, kid_activities, family_rooms, babysitting
    description = db.Column(db.Text)
    age_range = db.Column(db.String(20))  # 0-2, 3-5, 6-12, 13-17
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    destination = db.relationship('Destination', backref='family_friendly_features')

# Business Travel Features Models
class CorporateBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    corporate_account_id = db.Column(db.Integer, db.ForeignKey('corporate_account.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    approval_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)
    corporate_account = db.relationship('CorporateAccount', backref='corporate_bookings')
    employee = db.relationship('User', foreign_keys=[employee_id], backref='corporate_bookings')
    booking = db.relationship('Booking', backref='corporate_booking')
    approver = db.relationship('User', foreign_keys=[approver_id], backref='approved_bookings')

class ExpenseReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    corporate_account_id = db.Column(db.Integer, db.ForeignKey('corporate_account.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    report_name = db.Column(db.String(100), nullable=False)
    trip_purpose = db.Column(db.String(200))
    total_amount = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='draft')  # draft, submitted, approved, paid
    submitted_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    corporate_account = db.relationship('CorporateAccount', backref='expense_reports')
    employee = db.relationship('User', backref='expense_reports')
    expenses = db.relationship('ExpenseItem', backref='expense_report', lazy=True, cascade='all, delete-orphan')

class ExpenseItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_report_id = db.Column(db.Integer, db.ForeignKey('expense_report.id'), nullable=False)
    category = db.Column(db.String(50))  # flight, hotel, meals, transport, other
    description = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    receipt_url = db.Column(db.String(500))
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TravelPolicy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    corporate_account_id = db.Column(db.Integer, db.ForeignKey('corporate_account.id'), nullable=False)
    policy_name = db.Column(db.String(100), nullable=False)
    max_flight_cost = db.Column(db.Float)
    max_hotel_cost_per_night = db.Column(db.Float)
    max_meal_cost_per_day = db.Column(db.Float)
    allowed_airlines = db.Column(db.Text)  # JSON array
    allowed_hotel_chains = db.Column(db.Text)  # JSON array
    advance_booking_days = db.Column(db.Integer)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    corporate_account = db.relationship('CorporateAccount', backref='travel_policies')

class MeetingRoom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hotel_id = db.Column(db.Integer, db.ForeignKey('hotel.id'), nullable=False)
    room_name = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    equipment = db.Column(db.Text)  # JSON with available equipment
    price_per_hour = db.Column(db.Float, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    hotel = db.relationship('Hotel', backref='meeting_rooms')

class BusinessAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    corporate_account_id = db.Column(db.Integer, db.ForeignKey('corporate_account.id'), nullable=False)
    metric_type = db.Column(db.String(50))  # total_spend, avg_booking_value, popular_destinations
    metric_value = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(20))  # daily, weekly, monthly, quarterly
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    corporate_account = db.relationship('CorporateAccount', backref='business_analytics')

# Advanced Payment & Financial Models
class BuyNowPayLater(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    provider = db.Column(db.String(50))  # klarna, afterpay, affirm
    total_amount = db.Column(db.Float, nullable=False)
    installment_count = db.Column(db.Integer, nullable=False)
    installment_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='pending')  # pending, approved, active, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='buy_now_pay_later')

class TravelCreditCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    card_program = db.Column(db.String(100))  # airline, hotel, general travel
    card_name = db.Column(db.String(100), nullable=False)
    points_balance = db.Column(db.Integer, default=0)
    annual_fee = db.Column(db.Float, default=0.0)
    signup_bonus = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='travel_credit_cards')

class SplitPayment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    split_count = db.Column(db.Integer, nullable=False)
    amount_per_person = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, partial, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='split_payments')
    participants = db.relationship('SplitPaymentParticipant', backref='split_payment', lazy=True, cascade='all, delete-orphan')

class SplitPaymentParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    split_payment_id = db.Column(db.Integer, db.ForeignKey('split_payment.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount_paid = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid
    paid_at = db.Column(db.DateTime)
    user = db.relationship('User', backref='split_payment_participations')

class CurrencyHedging(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    original_currency = db.Column(db.String(10), nullable=False)
    hedged_currency = db.Column(db.String(10), nullable=False)
    original_amount = db.Column(db.Float, nullable=False)
    hedged_amount = db.Column(db.Float, nullable=False)
    exchange_rate = db.Column(db.Float, nullable=False)
    hedge_fee = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='currency_hedging')

class ExpenseTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trip_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))  # accommodation, transport, food, activities, shopping
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    receipt_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='expense_tracking')

# Post-Booking Experience Models
class DigitalDocument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    document_type = db.Column(db.String(50))  # visa, health_certificate, boarding_pass, itinerary
    document_url = db.Column(db.String(500), nullable=False)
    document_number = db.Column(db.String(100))
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    is_valid = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='digital_documents')

class PreTripPlanning(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trip_name = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    planning_status = db.Column(db.String(20), default='in_progress')  # in_progress, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='pre_trip_planning')
    checklists = db.relationship('PlanningChecklist', backref='planning', lazy=True, cascade='all, delete-orphan')

class PlanningChecklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    planning_id = db.Column(db.Integer, db.ForeignKey('pre_trip_planning.id'), nullable=False)
    category = db.Column(db.String(50))  # documents, packing, bookings, activities
    item_name = db.Column(db.String(200), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.Date)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high
    notes = db.Column(db.Text)

class TravelUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    update_type = db.Column(db.String(50))  # delay, gate_change, cancellation, weather
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20))  # low, medium, high, critical
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='travel_updates')

class InDestinationSupport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    support_type = db.Column(db.String(50))  # emergency, translation, local_info, transport
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200))
    contact_number = db.Column(db.String(20))
    status = db.Column(db.String(20), default='open')  # open, in_progress, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    booking = db.relationship('Booking', backref='in_destination_support')

class TravelDisruption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    disruption_type = db.Column(db.String(50))  # flight_cancellation, hotel_overbooking, weather
    description = db.Column(db.Text, nullable=False)
    impact_level = db.Column(db.String(20))  # minor, moderate, major
    compensation_offered = db.Column(db.Float, default=0.0)
    alternative_offered = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='reported')  # reported, processing, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    booking = db.relationship('Booking', backref='travel_disruptions')

class PostTripFeedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    overall_rating = db.Column(db.Integer, nullable=False)
    flight_rating = db.Column(db.Integer)
    hotel_rating = db.Column(db.Integer)
    service_rating = db.Column(db.Integer)
    value_rating = db.Column(db.Integer)
    comments = db.Column(db.Text)
    would_recommend = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    booking = db.relationship('Booking', backref='post_trip_feedback')

# Advanced Technology Models
class VoiceBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    voice_query = db.Column(db.Text, nullable=False)
    interpreted_query = db.Column(db.Text)
    booking_type = db.Column(db.String(50))  # flight, hotel, package
    confidence_score = db.Column(db.Float)
    is_successful = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='voice_bookings')

class BiometricAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    auth_type = db.Column(db.String(20))  # fingerprint, face_id, voice
    device_info = db.Column(db.Text)  # JSON with device details
    is_enabled = db.Column(db.Boolean, default=False)
    last_used = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='biometric_auth')

class IoTDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    device_type = db.Column(db.String(50))  # smart_luggage, travel_tracker, smart_watch
    device_id = db.Column(db.String(100), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    last_location = db.Column(db.Text)  # JSON with location data
    battery_level = db.Column(db.Integer)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='iot_devices')

class PredictiveAnalytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metric_type = db.Column(db.String(50))  # demand_forecast, price_prediction, user_behavior
    data_source = db.Column(db.String(100))
    prediction_value = db.Column(db.Float, nullable=False)
    confidence_interval = db.Column(db.Float)
    prediction_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Enterprise Features Models
class WhiteLabelPartner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partner_name = db.Column(db.String(200), nullable=False)
    domain = db.Column(db.String(200), unique=True, nullable=False)
    branding_config = db.Column(db.Text)  # JSON with branding settings
    commission_rate = db.Column(db.Float, default=0.05)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    users = db.relationship('User', backref='white_label_partner')

class APIMarketplace(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_name = db.Column(db.String(100), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    endpoint_url = db.Column(db.String(500), nullable=False)
    api_key = db.Column(db.String(200))
    rate_limit = db.Column(db.Integer)  # requests per minute
    pricing_model = db.Column(db.String(50))  # free, pay_per_use, subscription
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    usage_logs = db.relationship('APIUsageLog', backref='api_marketplace')

class MultiTenantConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.String(100), unique=True, nullable=False)
    tenant_name = db.Column(db.String(200), nullable=False)
    database_url = db.Column(db.String(500))
    custom_domain = db.Column(db.String(200))
    features_enabled = db.Column(db.Text)  # JSON with enabled features
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RevenueManagement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    revenue_type = db.Column(db.String(50))  # booking, commission, subscription, advertising
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='USD')
    source = db.Column(db.String(100))
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PartnerPortal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partner_name = db.Column(db.String(200), nullable=False)
    partner_type = db.Column(db.String(50))  # airline, hotel, tour_operator, affiliate
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    commission_rate = db.Column(db.Float, default=0.0)
    total_bookings = db.Column(db.Integer, default=0)
    total_revenue = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow) 

# --- STUBS FOR MISSING MODELS AND FUNCTIONS (added for app.py compatibility) ---
from db import db
from datetime import datetime

class LoyaltyTier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True)
    min_points = db.Column(db.Integer, default=0)
    discount_percentage = db.Column(db.Float, default=0.0)
    benefits = db.Column(db.Text)
    color = db.Column(db.String(20))

class UserLoyalty(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    tier_id = db.Column(db.Integer, db.ForeignKey('loyalty_tier.id'))
    points_balance = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    tier = db.relationship('LoyaltyTier', backref='user_loyalties')

class LoyaltyTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    points = db.Column(db.Integer, default=0)
    transaction_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    booking_id = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CustomerLifetimeValue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_revenue = db.Column(db.Float, default=0.0)
    total_orders = db.Column(db.Integer, default=0)
    average_order_value = db.Column(db.Float, default=0.0)
    first_purchase_date = db.Column(db.DateTime)
    last_purchase_date = db.Column(db.DateTime)
    predicted_lifetime_value = db.Column(db.Float, default=0.0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

class PriceAlert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'))
    target_price = db.Column(db.Float)
    current_price = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TwoFactorAuth(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    secret_key = db.Column(db.String(100))
    is_enabled = db.Column(db.Boolean, default=False)

class CorporateEmployee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    corporate_account_id = db.Column(db.Integer, db.ForeignKey('corporate_account.id'))
    position = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)

class CorporateAccount(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200))
    contact_email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Utility function stubs ---
def log_error(context, message):
    print(f"[ERROR] {context}: {message}")

def get_flight_tracking(flight_number):
    return None

def get_hotel_availability(hotel_id, check_in, check_out):
    return None

def calculate_dynamic_pricing(destination_id, travel_date, demand_factor):
    return 100.0

def track_user_behavior(user_id, session_id, page_url, action_type, action_data):
    pass

def get_personalized_recommendations_ml(user_id, limit=6):
    return []

def generate_boarding_pass(booking_id, passenger_name, flight_number):
    class BoardingPass:
        def __init__(self, passenger_name, flight_number):
            self.id = 1
            self.qr_code = "dummy_qr_code"
            self.passenger_name = passenger_name
            self.flight_number = flight_number
    return BoardingPass(passenger_name, flight_number)

def create_support_ticket(user_id, subject, description, category, priority):
    class Ticket:
        def __init__(self, subject):
            self.id = 1
            self.subject = subject
            self.status = "open"
            self.created_at = datetime.utcnow()
    return Ticket(subject)

def generate_2fa_secret():
    return "DUMMYSECRET"

def verify_2fa_code(secret_key, code):
    return True

def track_conversion_funnel(funnel_name, step_name, step_order, user_id):
    pass

def send_notification_task(user_id, title, message, notification_type):
    pass 

# --- Minimal APIUsageLog model for APIMarketplace relationship ---
class APIUsageLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_marketplace_id = db.Column(db.Integer, db.ForeignKey('api_marketplace.id'))
    usage_time = db.Column(db.DateTime, default=datetime.utcnow)
    request_count = db.Column(db.Integer, default=0) 