"""
Payment service layer for business logic
"""
import random
from typing import List, Optional
from datetime import datetime
from app.models import db, PaymentTransaction, PaymentType, Policy


class PaymentService:
    """Service class for payment-related business logic"""

    @staticmethod
    def get_all_payments() -> List[PaymentTransaction]:
        """Get all payment transactions from the database"""
        return PaymentTransaction.query.all()

    @staticmethod
    def get_payment_by_id(payment_id: int) -> Optional[PaymentTransaction]:
        """Get a payment transaction by ID"""
        return PaymentTransaction.query.get(payment_id)

    @staticmethod
    def create_payment(policy_id: int, payment_type: str) -> Optional[PaymentTransaction]:
        """Create a new payment transaction"""
        # Validate policy exists
        policy = Policy.query.get(policy_id)
        if not policy:
            raise ValueError("Policy not found")
        
        # Convert string to enum
        try:
            payment_type_enum = PaymentType(payment_type)
        except ValueError:
            raise ValueError(f"Invalid payment type: {payment_type}")
        
        # Simulate payment processing
        success = PaymentService._process_payment(payment_type_enum)
        
        payment = PaymentTransaction(
            time=datetime.utcnow(),
            payment_type=payment_type_enum,
            policy_id=policy_id,
            success=success
        )
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def get_payments_by_policy(policy_id: int) -> List[PaymentTransaction]:
        """Get all payment transactions for a specific policy"""
        return PaymentTransaction.query.filter_by(policy_id=policy_id).all()

    @staticmethod
    def get_successful_payments() -> List[PaymentTransaction]:
        """Get all successful payment transactions"""
        return PaymentTransaction.query.filter_by(success=True).all()

    @staticmethod
    def get_failed_payments() -> List[PaymentTransaction]:
        """Get all failed payment transactions"""
        return PaymentTransaction.query.filter_by(success=False).all()

    @staticmethod
    def get_payments_by_type(payment_type: PaymentType) -> List[PaymentTransaction]:
        """Get all payment transactions of a specific type"""
        return PaymentTransaction.query.filter_by(payment_type=payment_type).all()

    @staticmethod
    def _process_payment(payment_type: PaymentType) -> bool:
        """
        Simulate payment processing with different success rates by type
        In a real system, this would integrate with payment processors
        """
        success_rates = {
            PaymentType.CREDIT: 0.85,  # 85% success rate
            PaymentType.DEBIT: 0.90,   # 90% success rate
            PaymentType.PREPAID: 0.75  # 75% success rate
        }
        
        success_rate = success_rates.get(payment_type, 0.80)
        return random.random() < success_rate
