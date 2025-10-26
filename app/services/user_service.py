"""
User service layer for business logic
"""
from typing import List, Optional
from app.models import db, User


class UserService:
    """Service class for user-related business logic"""

    @staticmethod
    def get_all_users() -> List[User]:
        """Get all users from the database"""
        return User.query.all()

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get a user by ID"""
        return User.query.get(user_id)

    @staticmethod
    def create_user(name: str, email: Optional[str] = None) -> User:
        """Create a new user"""
        user = User(name=name, email=email)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update_user(user_id: int, name: Optional[str] = None, email: Optional[str] = None) -> Optional[User]:
        """Update an existing user"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        
        db.session.commit()
        return user

    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete a user by ID"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        db.session.delete(user)
        db.session.commit()
        return True

    @staticmethod
    def user_exists(user_id: int) -> bool:
        """Check if a user exists"""
        return User.query.get(user_id) is not None
