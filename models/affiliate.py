"""
Affiliate Click Tracking Model
"""
from datetime import datetime
from db import db

class AffiliateClick(db.Model):
    __tablename__ = 'affiliate_clicks'
    
    id = db.Column(db.Integer, primary_key=True)
    affiliate_type = db.Column(db.String(50), nullable=False)  # 'booking', 'skyscanner', 'insurance'
    destination = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)
    converted = db.Column(db.Boolean, default=False)  # Track if click led to booking
    commission_earned = db.Column(db.Float, default=0.0)
    
    def __repr__(self):
        return f'<AffiliateClick {self.affiliate_type} - {self.destination}>'
