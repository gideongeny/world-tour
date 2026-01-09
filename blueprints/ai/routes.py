from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from db import db
from new_models import AITravelAssistant
import json
from services.ai_engine import ai_engine
from new_models import UserAnalytics
from datetime import datetime

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/api/chat', methods=['POST'])
def ai_chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user context
        user_context = {
            'user_id': current_user.id if current_user.is_authenticated else 'guest',
            'username': current_user.username if current_user.is_authenticated else 'Guest'
        }
        
        # Generate AI response
        ai_response = ai_engine.generate_response(user_message, context=user_context)
        
        # Save conversation to database if logged in
        if current_user.is_authenticated:
            conversation = AITravelAssistant(
                user_id=current_user.id,
                query=user_message,
                response=ai_response
            )
            db.session.add(conversation)
            
            # Log user analytics
            user_analytics = UserAnalytics(
                user_id=current_user.id,
                event_type='AI_CHAT_MESSAGE',
                event_details={'query': user_message, 'response': ai_response},
                timestamp=datetime.utcnow()
            )
            db.session.add(user_analytics)
            db.session.commit()
        
        return jsonify({'status': 'success', 'response': ai_response})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
