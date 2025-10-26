"""
Unit tests for database models
"""
import pytest
from datetime import datetime
from app.models import db, User, Quote, Policy, PaymentTransaction, PaymentType


class TestUser:
    """Test User model"""
    
    def test_create_user(self, app):
        """Test creating a user"""
        with app.app_context():
            user = User(name="John Doe", email="john@example.com")
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.name == "John Doe"
            assert user.email == "john@example.com"
    
    def test_user_repr(self, app):
        """Test user string representation"""
        with app.app_context():
            user = User(name="Jane Smith")
            assert str(user) == "<User Jane Smith>"
    
    def test_user_relationships(self, app, sample_user):
        """Test user relationships"""
        with app.app_context():
            # Create quote for user
            quote = Quote(user_id=sample_user.id, create_time=datetime.utcnow())
            db.session.add(quote)
            db.session.commit()
            
            # Test relationship
            user = User.query.get(sample_user.id)
            assert len(user.quotes) == 1
            assert user.quotes[0].id == quote.id


class TestQuote:
    """Test Quote model"""
    
    def test_create_quote(self, app, sample_user):
        """Test creating a quote"""
        with app.app_context():
            quote = Quote(
                user_id=sample_user.id,
                create_time=datetime.utcnow(),
                bindable=True
            )
            db.session.add(quote)
            db.session.commit()
            
            assert quote.id is not None
            assert quote.user_id == sample_user.id
            assert quote.bindable is True
            assert quote.bind_time is None
    
    def test_quote_repr(self, app, sample_quote):
        """Test quote string representation"""
        with app.app_context():
            quote = Quote.query.get(sample_quote.id)
            expected = f"<Quote {quote.id} for User {quote.user_id}>"
            assert str(quote) == expected
    
    def test_bind_quote(self, app, sample_quote):
        """Test binding a quote"""
        with app.app_context():
            quote = Quote.query.get(sample_quote.id)
            bind_time = datetime.utcnow()
            quote.bind_time = bind_time
            db.session.commit()
            
            updated_quote = Quote.query.get(sample_quote.id)
            assert updated_quote.bind_time is not None


class TestPolicy:
    """Test Policy model"""
    
    def test_create_policy(self, app, sample_user, bound_quote):
        """Test creating a policy"""
        with app.app_context():
            policy = Policy(
                user_id=sample_user.id,
                quote_id=bound_quote.id
            )
            db.session.add(policy)
            db.session.commit()
            
            assert policy.id is not None
            assert policy.user_id == sample_user.id
            assert policy.quote_id == bound_quote.id
    
    def test_policy_repr(self, app, sample_policy):
        """Test policy string representation"""
        with app.app_context():
            policy = Policy.query.get(sample_policy.id)
            expected = f"<Policy {policy.id} for User {policy.user_id}>"
            assert str(policy) == expected


class TestPaymentTransaction:
    """Test PaymentTransaction model"""
    
    def test_create_payment(self, app, sample_policy):
        """Test creating a payment transaction"""
        with app.app_context():
            payment = PaymentTransaction(
                time=datetime.utcnow(),
                payment_type=PaymentType.CREDIT,
                policy_id=sample_policy.id,
                success=True
            )
            db.session.add(payment)
            db.session.commit()
            
            assert payment.id is not None
            assert payment.payment_type == PaymentType.CREDIT
            assert payment.policy_id == sample_policy.id
            assert payment.success is True
    
    def test_payment_repr(self, app, sample_payment):
        """Test payment string representation"""
        with app.app_context():
            payment = PaymentTransaction.query.get(sample_payment.id)
            expected = f"<PaymentTransaction {payment.id} for Policy {payment.policy_id}>"
            assert str(payment) == expected
    
    def test_payment_type_enum(self):
        """Test PaymentType enum values"""
        assert PaymentType.CREDIT.value == "Credit"
        assert PaymentType.DEBIT.value == "Debit"
        assert PaymentType.PREPAID.value == "Prepaid"
