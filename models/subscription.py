"""
Subscription Model - Premium Membership
"""
from datetime import datetime
from extensions import db

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    
    # Subscription details
    plan = db.Column(db.String(20), nullable=False)  # 'monthly' or 'yearly'
    status = db.Column(db.String(20), default='active')  # 'active', 'cancelled', 'expired', 'past_due'
    
    # Stripe integration
    stripe_customer_id = db.Column(db.String(100))
    stripe_subscription_id = db.Column(db.String(100))
    
    # Billing
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('subscription', uselist=False))
    
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'active' and self.current_period_end > datetime.utcnow()
    
    def __repr__(self):
        return f'<Subscription {self.user_id} - {self.plan} - {self.status}>'
