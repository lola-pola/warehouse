"""
Quote service layer for business logic
"""
from typing import List, Optional
from datetime import datetime
from app.models import db, Quote, User


class QuoteService:
    """Service class for quote-related business logic"""

    @staticmethod
    def get_all_quotes() -> List[Quote]:
        """Get all quotes from the database"""
        return Quote.query.all()

    @staticmethod
    def get_quote_by_id(quote_id: int) -> Optional[Quote]:
        """Get a quote by ID"""
        return Quote.query.get(quote_id)

    @staticmethod
    def create_quote(user_id: int, bindable: bool = True) -> Optional[Quote]:
        """Create a new quote for a user"""
        # Validate user exists
        user = User.query.get(user_id)
        if not user:
            return None
        
        quote = Quote(
            user_id=user_id,
            create_time=datetime.utcnow(),
            bindable=bindable
        )
        db.session.add(quote)
        db.session.commit()
        return quote

    @staticmethod
    def bind_quote(quote_id: int) -> Optional[Quote]:
        """Bind a quote (set bind_time)"""
        quote = Quote.query.get(quote_id)
        if not quote:
            return None
        
        if not quote.bindable:
            raise ValueError("Quote is not bindable")
        
        if quote.bind_time:
            raise ValueError("Quote is already bound")
        
        quote.bind_time = datetime.utcnow()
        db.session.commit()
        return quote

    @staticmethod
    def get_quotes_by_user(user_id: int) -> List[Quote]:
        """Get all quotes for a specific user"""
        return Quote.query.filter_by(user_id=user_id).all()

    @staticmethod
    def get_bindable_quotes() -> List[Quote]:
        """Get all bindable quotes that haven't been bound yet"""
        return Quote.query.filter_by(bindable=True, bind_time=None).all()

    @staticmethod
    def is_quote_bound(quote_id: int) -> bool:
        """Check if a quote is bound"""
        quote = Quote.query.get(quote_id)
        return quote and quote.bind_time is not None
