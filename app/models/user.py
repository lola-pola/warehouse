"""
User model for the data warehouse
"""
from .base import db


class User(db.Model):
    """User model representing insurance customers"""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    
    # Relationships
    quotes = db.relationship("Quote", back_populates="user", lazy=True)
    policies = db.relationship("Policy", back_populates="user", lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'
