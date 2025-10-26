"""
Unit tests for service layer
"""
import pytest
from datetime import datetime
from app.services import UserService, QuoteService, PolicyService, PaymentService, AnalyticsService
from app.models import User, Quote, Policy, PaymentTransaction, PaymentType


class TestUserService:
    """Test UserService"""
    
    def test_create_user(self, app):
        """Test creating a user through service"""
        with app.app_context():
            user = UserService.create_user("John Doe", "john@example.com")
            
            assert user.id is not None
            assert user.name == "John Doe"
            assert user.email == "john@example.com"
    
    def test_get_user_by_id(self, app, sample_user):
        """Test getting user by ID"""
        with app.app_context():
            user = UserService.get_user_by_id(sample_user.id)
            
            assert user is not None
            assert user.id == sample_user.id
            assert user.name == sample_user.name
    
    def test_get_nonexistent_user(self, app):
        """Test getting non-existent user"""
        with app.app_context():
            user = UserService.get_user_by_id(999)
            assert user is None
    
    def test_update_user(self, app, sample_user):
        """Test updating user"""
        with app.app_context():
            updated_user = UserService.update_user(
                sample_user.id, 
                name="Updated Name",
                email="updated@example.com"
            )
            
            assert updated_user is not None
            assert updated_user.name == "Updated Name"
            assert updated_user.email == "updated@example.com"
    
    def test_delete_user(self, app, sample_user):
        """Test deleting user"""
        with app.app_context():
            result = UserService.delete_user(sample_user.id)
            assert result is True
            
            # Verify user is deleted
            user = UserService.get_user_by_id(sample_user.id)
            assert user is None
    
    def test_user_exists(self, app, sample_user):
        """Test checking if user exists"""
        with app.app_context():
            assert UserService.user_exists(sample_user.id) is True
            assert UserService.user_exists(999) is False


class TestQuoteService:
    """Test QuoteService"""
    
    def test_create_quote(self, app, sample_user):
        """Test creating a quote through service"""
        with app.app_context():
            quote = QuoteService.create_quote(sample_user.id, bindable=True)
            
            assert quote is not None
            assert quote.user_id == sample_user.id
            assert quote.bindable is True
            assert quote.create_time is not None
    
    def test_create_quote_invalid_user(self, app):
        """Test creating quote with invalid user"""
        with app.app_context():
            quote = QuoteService.create_quote(999, bindable=True)
            assert quote is None
    
    def test_bind_quote(self, app, sample_quote):
        """Test binding a quote"""
        with app.app_context():
            bound_quote = QuoteService.bind_quote(sample_quote.id)
            
            assert bound_quote is not None
            assert bound_quote.bind_time is not None
    
    def test_bind_nonbindable_quote(self, app, sample_user):
        """Test binding a non-bindable quote"""
        with app.app_context():
            # Create non-bindable quote
            quote = Quote(
                user_id=sample_user.id,
                create_time=datetime.utcnow(),
                bindable=False
            )
            quote = QuoteService.create_quote(sample_user.id, bindable=False)
            
            with pytest.raises(ValueError, match="Quote is not bindable"):
                QuoteService.bind_quote(quote.id)


class TestPolicyService:
    """Test PolicyService"""
    
    def test_create_policy(self, app, sample_user, bound_quote):
        """Test creating a policy through service"""
        with app.app_context():
            policy = PolicyService.create_policy(sample_user.id, bound_quote.id)
            
            assert policy is not None
            assert policy.user_id == sample_user.id
            assert policy.quote_id == bound_quote.id
    
    def test_create_policy_unbound_quote(self, app, sample_user, sample_quote):
        """Test creating policy with unbound quote"""
        with app.app_context():
            with pytest.raises(ValueError, match="Quote must be bound"):
                PolicyService.create_policy(sample_user.id, sample_quote.id)
    
    def test_create_policy_wrong_user(self, app, bound_quote):
        """Test creating policy with wrong user"""
        with app.app_context():
            # Create another user
            other_user = User(name="Other User")
            from app.models import db
            db.session.add(other_user)
            db.session.commit()
            
            with pytest.raises(ValueError, match="Quote does not belong"):
                PolicyService.create_policy(other_user.id, bound_quote.id)


class TestPaymentService:
    """Test PaymentService"""
    
    def test_create_payment(self, app, sample_policy):
        """Test creating a payment through service"""
        with app.app_context():
            payment = PaymentService.create_payment(sample_policy.id, "CREDIT")
            
            assert payment is not None
            assert payment.policy_id == sample_policy.id
            assert payment.payment_type == PaymentType.CREDIT
            assert payment.time is not None
            assert payment.success in [True, False]  # Random success
    
    def test_create_payment_invalid_type(self, app, sample_policy):
        """Test creating payment with invalid type"""
        with app.app_context():
            with pytest.raises(ValueError, match="Invalid payment type"):
                PaymentService.create_payment(sample_policy.id, "INVALID")
    
    def test_create_payment_invalid_policy(self, app):
        """Test creating payment with invalid policy"""
        with app.app_context():
            with pytest.raises(ValueError, match="Policy not found"):
                PaymentService.create_payment(999, "CREDIT")


class TestAnalyticsService:
    """Test AnalyticsService"""
    
    def test_get_general_stats(self, app, sample_user, sample_quote, sample_policy, sample_payment):
        """Test getting general statistics"""
        with app.app_context():
            stats = AnalyticsService.get_general_stats()
            
            assert 'total_users' in stats
            assert 'total_quotes' in stats
            assert 'total_policies' in stats
            assert 'total_payments' in stats
            assert 'successful_payments' in stats
            assert 'payment_success_rate' in stats
            
            assert stats['total_users'] >= 1
            assert stats['total_quotes'] >= 1
            assert stats['total_policies'] >= 1
            assert stats['total_payments'] >= 1
    
    def test_get_payment_stats_by_type(self, app, sample_payment):
        """Test getting payment statistics by type"""
        with app.app_context():
            stats = AnalyticsService.get_payment_stats_by_type()
            
            assert isinstance(stats, dict)
            assert 'Credit' in stats
            assert 'Debit' in stats
            assert 'Prepaid' in stats
            
            # Check structure of payment type stats
            credit_stats = stats['Credit']
            assert 'total' in credit_stats
            assert 'successful' in credit_stats
            assert 'failed' in credit_stats
            assert 'success_rate' in credit_stats
