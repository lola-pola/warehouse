"""
Policy model for the data warehouse
"""
from .base import db


class Policy(db.Model):
    """Policy model representing insurance policies"""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quote_id = db.Column(db.Integer, db.ForeignKey("quote.id"), nullable=False)
    
    # Relationships
    user = db.relationship("User", back_populates="policies")
    quote = db.relationship("Quote", back_populates="policies")
    payment_transactions = db.relationship("PaymentTransaction", back_populates="policy", lazy=True)
    
    def __repr__(self):
        return f'<Policy {self.id} for User {self.user_id}>'
