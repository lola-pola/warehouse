"""
Policy service layer for business logic
"""
from typing import List, Optional
from app.models import db, Policy, User, Quote


class PolicyService:
    """Service class for policy-related business logic"""

    @staticmethod
    def get_all_policies() -> List[Policy]:
        """Get all policies from the database"""
        return Policy.query.all()

    @staticmethod
    def get_policy_by_id(policy_id: int) -> Optional[Policy]:
        """Get a policy by ID"""
        return Policy.query.get(policy_id)

    @staticmethod
    def create_policy(user_id: int, quote_id: int) -> Optional[Policy]:
        """Create a new policy from a quote"""
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Validate quote exists
        quote = Quote.query.get(quote_id)
        if not quote:
            raise ValueError("Quote not found")
        
        # Validate quote belongs to user
        if quote.user_id != user_id:
            raise ValueError("Quote does not belong to the specified user")
        
        # Validate quote is bound
        if not quote.bind_time:
            raise ValueError("Quote must be bound before creating a policy")
        
        # Check if policy already exists for this quote
        existing_policy = Policy.query.filter_by(quote_id=quote_id).first()
        if existing_policy:
            raise ValueError("Policy already exists for this quote")
        
        policy = Policy(
            user_id=user_id,
            quote_id=quote_id
        )
        db.session.add(policy)
        db.session.commit()
        return policy

    @staticmethod
    def get_policies_by_user(user_id: int) -> List[Policy]:
        """Get all policies for a specific user"""
        return Policy.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_policy_by_quote(quote_id: int) -> Optional[Policy]:
        """Get policy associated with a specific quote"""
        return Policy.query.filter_by(quote_id=quote_id).first()

    @staticmethod
    def delete_policy(policy_id: int) -> bool:
        """Delete a policy by ID"""
        policy = Policy.query.get(policy_id)
        if not policy:
            return False
        
        db.session.delete(policy)
        db.session.commit()
        return True
