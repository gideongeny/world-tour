from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from db import db
from new_models import AITravelAssistant
import json
from services.ai_engine import ai_engine

ai_bp = Blueprint('ai', __name__)

@ai_bp.route('/api/chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    message = data.get('message')
    response_content = ai_engine.get_travel_recommendation(message, {})
    return jsonify({'status': 'success', 'response': response_content})
