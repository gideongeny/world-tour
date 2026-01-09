"""
Affiliate API Routes
Handles affiliate link generation and click tracking
"""
from flask import Blueprint, request, jsonify, redirect
from services.affiliate_service import AffiliateService
from models.affiliate import AffiliateClick
from extensions import db

affiliate_bp = Blueprint('affiliate', __name__, url_prefix='/api/affiliate')

@affiliate_bp.route('/track', methods=['POST'])
def track_click():
    """Track affiliate link click"""
    data = request.get_json()
    
    affiliate_type = data.get('affiliateType')
    destination = data.get('destination')
    user_id = data.get('userId')
    
    click_id = AffiliateService.track_click(affiliate_type, destination, user_id)
    
    return jsonify({'success': True, 'click_id': click_id}), 200

@affiliate_bp.route('/redirect', methods=['GET'])
def redirect_affiliate():
    """Generate and redirect to affiliate link"""
    link_type = request.args.get('type')
    
    if link_type == 'hotel':
        destination = request.args.get('destination')
        checkin = request.args.get('checkin')
        checkout = request.args.get('checkout')
        
        # Track click
        AffiliateService.track_click('booking', destination)
        
        # Generate and redirect
        url = AffiliateService.get_hotel_link(destination, checkin, checkout)
        return redirect(url)
    
    elif link_type == 'flight':
        origin = request.args.get('origin')
        destination = request.args.get('destination')
        date = request.args.get('date')
        
        # Track click
        AffiliateService.track_click('skyscanner', destination)
        
        # Generate and redirect
        url = AffiliateService.get_flight_link(origin, destination, date)
        return redirect(url)
    
    return jsonify({'error': 'Invalid link type'}), 400

@affiliate_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get affiliate performance stats"""
    total_clicks = AffiliateClick.query.count()
    conversions = AffiliateClick.query.filter_by(converted=True).count()
    total_commission = db.session.query(db.func.sum(AffiliateClick.commission_earned)).scalar() or 0
    
    return jsonify({
        'total_clicks': total_clicks,
        'conversions': conversions,
        'conversion_rate': (conversions / total_clicks * 100) if total_clicks > 0 else 0,
        'total_commission': float(total_commission)
    }), 200
