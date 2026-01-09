"""
Payment Routes - Subscription Management
"""
from flask import Blueprint, request, jsonify, redirect
from flask_login import login_required, current_user
from services.stripe_service import StripeService
from models.subscription import Subscription
from new_models import User
from extensions import db
from datetime import datetime
import stripe
import os

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

@payments_bp.route('/create-subscription', methods=['POST'])
@login_required
def create_subscription():
    """Create a new subscription"""
    data = request.get_json()
    plan = data.get('plan', 'monthly')  # 'monthly' or 'yearly'
    
    # Check if user already has subscription
    existing_sub = Subscription.query.filter_by(user_id=current_user.id).first()
    if existing_sub and existing_sub.is_active():
        return jsonify({'error': 'Already subscribed'}), 400
    
    # Create or get Stripe customer
    if not current_user.stripe_customer_id:
        customer_id = StripeService.create_customer(current_user.email, current_user.username)
        if not customer_id:
            return jsonify({'error': 'Failed to create customer'}), 500
        current_user.stripe_customer_id = customer_id
        db.session.commit()
    
    # Create checkout session
    checkout_url, session_id = StripeService.create_subscription_checkout(
        current_user.stripe_customer_id,
        plan
    )
    
    if not checkout_url:
        return jsonify({'error': 'Failed to create checkout'}), 500
    
    return jsonify({'checkout_url': checkout_url, 'session_id': session_id}), 200

@payments_bp.route('/create-paypal-payment', methods=['POST'])
@login_required
def create_paypal_payment():
    """Create a PayPal payment (simpler alternative to Stripe)"""
    from services.paypal_service import PayPalService
    
    data = request.get_json()
    amount = data.get('amount')
    plan_name = data.get('plan')
    
    # Create PayPal payment
    approval_url, order_id = PayPalService.create_payment(
        amount=amount,
        description=f"{plan_name} - World Tour Plus",
        return_url='http://localhost:5173/subscription/success',
        cancel_url='http://localhost:5173/pricing'
    )
    
    if not approval_url:
        return jsonify({'error': 'PayPal not configured. Add PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET to .env'}), 500
    
    return jsonify({'approval_url': approval_url, 'order_id': order_id}), 200

@payments_bp.route('/cancel-subscription', methods=['POST'])
@login_required
def cancel_subscription():
    """Cancel user's subscription"""
    subscription = Subscription.query.filter_by(user_id=current_user.id).first()
    
    if not subscription or not subscription.is_active():
        return jsonify({'error': 'No active subscription'}), 400
    
    # Cancel in Stripe
    success = StripeService.cancel_subscription(subscription.stripe_subscription_id)
    
    if success:
        subscription.cancel_at_period_end = True
        db.session.commit()
        return jsonify({'message': 'Subscription cancelled', 'ends_at': subscription.current_period_end}), 200
    
    return jsonify({'error': 'Failed to cancel subscription'}), 500

@payments_bp.route('/subscription-status', methods=['GET'])
@login_required
def subscription_status():
    """Get current subscription status"""
    subscription = Subscription.query.filter_by(user_id=current_user.id).first()
    
    if not subscription:
        return jsonify({'subscribed': False}), 200
    
    return jsonify({
        'subscribed': subscription.is_active(),
        'plan': subscription.plan,
        'status': subscription.status,
        'current_period_end': subscription.current_period_end.isoformat() if subscription.current_period_end else None,
        'cancel_at_period_end': subscription.cancel_at_period_end
    }), 200

@payments_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.environ.get('STRIPE_WEBHOOK_SECRET')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 400
    
    # Handle subscription events
    if event['type'] == 'customer.subscription.created':
        handle_subscription_created(event['data']['object'])
    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event['data']['object'])
    elif event['type'] == 'customer.subscription.deleted':
        handle_subscription_deleted(event['data']['object'])
    
    return jsonify({'success': True}), 200

def handle_subscription_created(subscription_data):
    """Handle new subscription creation"""
    customer_id = subscription_data['customer']
    user = User.query.filter_by(stripe_customer_id=customer_id).first()
    
    if user:
        subscription = Subscription(
            user_id=user.id,
            plan='monthly' if subscription_data['items']['data'][0]['plan']['interval'] == 'month' else 'yearly',
            status='active',
            stripe_customer_id=customer_id,
            stripe_subscription_id=subscription_data['id'],
            current_period_start=datetime.fromtimestamp(subscription_data['current_period_start']),
            current_period_end=datetime.fromtimestamp(subscription_data['current_period_end'])
        )
        db.session.add(subscription)
        db.session.commit()

def handle_subscription_updated(subscription_data):
    """Handle subscription updates"""
    subscription = Subscription.query.filter_by(
        stripe_subscription_id=subscription_data['id']
    ).first()
    
    if subscription:
        subscription.status = subscription_data['status']
        subscription.current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
        subscription.cancel_at_period_end = subscription_data.get('cancel_at_period_end', False)
        db.session.commit()

def handle_subscription_deleted(subscription_data):
    """Handle subscription cancellation"""
    subscription = Subscription.query.filter_by(
        stripe_subscription_id=subscription_data['id']
    ).first()
    
    if subscription:
        subscription.status = 'cancelled'
        db.session.commit()
