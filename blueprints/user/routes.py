from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from new_models import SavedItem, Destination, Hotel, Flight
from models.subscription import Subscription
from db import db
import json
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    # Build profile data
    subscription = Subscription.query.filter_by(user_id=current_user.id, active=True).first()
    saved_count = SavedItem.query.filter_by(user_id=current_user.id).count()
    
    return jsonify({
        'username': current_user.username,
        'email': current_user.email,
        'subscription': {
            'active': bool(subscription),
            'plan': subscription.plan_type if subscription else 'free',
            'expires_at': subscription.end_date.isoformat() if subscription else None
        },
        'stats': {
            'saved_trips': saved_count
        }
    })

@user_bp.route('/wishlist', methods=['GET'])
@login_required
def get_wishlist():
    items = SavedItem.query.filter_by(user_id=current_user.id).order_by(SavedItem.created_at.desc()).all()
    results = []
    
    for item in items:
        # Load item data
        data = {}
        if item.item_data:
            try:
                data = json.loads(item.item_data)
            except:
                pass
        
        # If destination_id exists, fetch destination details (to ensure fresh data)
        if item.destination_id:
            dest = Destination.query.get(item.destination_id)
            if dest:
                # Merge dest data, preferring DB data over snapshot for these fields
                data['name'] = dest.name
                data['country'] = dest.country
                data['image_url'] = dest.image_url
                data['id'] = dest.id
                data['rating'] = dest.rating
                
        results.append({
            'id': item.id,
            'type': item.item_type,
            'data': data,
            'created_at': item.created_at.isoformat()
        })
        
    return jsonify(results)

@user_bp.route('/wishlist', methods=['POST'])
@login_required
def add_wishlist():
    data = request.get_json()
    item_type = data.get('type')
    item_data_raw = data.get('data', {})
    
    # Validation
    if not item_type:
        return jsonify({'error': 'Item type required'}), 400

    new_item = SavedItem(
        user_id=current_user.id,
        item_type=item_type,
        item_data=json.dumps(item_data_raw)
    )
    
    # Handle specific types
    if item_type == 'destination' and 'id' in item_data_raw:
         # Try to link to DB ID if provided
        try:
            dest_id = int(item_data_raw['id'])
            new_item.destination_id = dest_id
        except:
            pass # Keep as unlinked if ID is weird
            
    # Save
    db.session.add(new_item)
    db.session.commit()
    
    return jsonify({'success': True, 'id': new_item.id}), 201

@user_bp.route('/wishlist/<int:id>', methods=['DELETE'])
@login_required
def remove_wishlist(id):
    item = SavedItem.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})
