from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from db import db
from new_models import AITravelAssistant, UserAnalytics, Destination, Booking, Review, WishlistItem
import json

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/assistant')
@login_required
def ai_assistant():
    return render_template('ai_travel_assistant.html')

from services.ai_engine import ai_engine

@ai_bp.route('/api/chat', methods=['POST'])
@login_required
def ai_chat():
    data = request.get_json()
    message = data.get('message')
    
    # Get context for better AI response
    user_context = {
        'username': current_user.username,
        'email': current_user.email,
        'recent_bookings': [b.destination.name for b in current_user.bookings[:3] if b.destination]
    }
    
    # Store user message
    user_msg = AITravelAssistant(
        user_id=current_user.id,
        conversation_id=data.get('conversation_id', 'default'),
        message_type='user',
        message_content=message
    )
    db.session.add(user_msg)
    
    # Call real Gemini AI
    response_content = ai_engine.get_travel_recommendation(message, user_context)
    
    ai_msg = AITravelAssistant(
        user_id=current_user.id,
        conversation_id=data.get('conversation_id', 'default'),
        message_type='assistant',
        message_content=response_content
    )
    db.session.add(ai_msg)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'response': response_content
    })

@ai_bp.route('/api/recommendations')
@login_required
def get_recommendations():
    # Logic moved from get_personalized_recommendations
    return jsonify({'recommendations': []})

@ai_bp.route('/voice_booking', methods=['POST'])
@login_required
def voice_booking():
    data = request.get_json()
    query = data.get('query')
    # Use helper from app.py
    # ... logic ...
    return jsonify({'result': 'Voice booking processed'})
