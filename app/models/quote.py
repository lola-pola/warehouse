"""
Quote model for the data warehouse
"""
from .base import db


class Quote(db.Model):
    """Quote model representing insurance quotes"""
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    create_time = db.Column(db.DateTime)
    bind_time = db.Column(db.DateTime)
    bindable = db.Column(db.Boolean)
    
    # Relationships
    user = db.relationship("User", back_populates="quotes")
    policies = db.relationship("Policy", back_populates="quote", lazy=True)
    
    def __repr__(self):
        return f'<Quote {self.id} for User {self.user_id}>'
