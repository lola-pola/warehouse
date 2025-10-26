"""
Payment models and enums for the data warehouse
"""
import enum
from .base import db


class PaymentType(enum.Enum):
    """Enum for different payment types"""
    CREDIT = "Credit"
    DEBIT = "Debit"
    PREPAID = "Prepaid"


class PaymentTransaction(db.Model):
    """Payment transaction model representing payment attempts"""
    
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    payment_type = db.Column(db.Enum(PaymentType))
    policy_id = db.Column(db.Integer, db.ForeignKey("policy.id"), nullable=False)
    success = db.Column(db.Boolean)
    
    # Relationships
    policy = db.relationship("Policy", back_populates="payment_transactions")
    
    def __repr__(self):
        return f'<PaymentTransaction {self.id} for Policy {self.policy_id}>'
