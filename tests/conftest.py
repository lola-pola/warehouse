"""
Test configuration and fixtures
"""
import pytest
from app import create_app
from app.models import db, User, Quote, Policy, PaymentTransaction, PaymentType
from datetime import datetime


@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing"""
    with app.app_context():
        user = User(name="Test User", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_quote(app, sample_user):
    """Create a sample quote for testing"""
    with app.app_context():
        quote = Quote(
            user_id=sample_user.id,
            create_time=datetime.utcnow(),
            bindable=True
        )
        db.session.add(quote)
        db.session.commit()
        return quote


@pytest.fixture
def bound_quote(app, sample_user):
    """Create a bound quote for testing"""
    with app.app_context():
        quote = Quote(
            user_id=sample_user.id,
            create_time=datetime.utcnow(),
            bind_time=datetime.utcnow(),
            bindable=True
        )
        db.session.add(quote)
        db.session.commit()
        return quote


@pytest.fixture
def sample_policy(app, sample_user, bound_quote):
    """Create a sample policy for testing"""
    with app.app_context():
        policy = Policy(
            user_id=sample_user.id,
            quote_id=bound_quote.id
        )
        db.session.add(policy)
        db.session.commit()
        return policy


@pytest.fixture
def sample_payment(app, sample_policy):
    """Create a sample payment for testing"""
    with app.app_context():
        payment = PaymentTransaction(
            time=datetime.utcnow(),
            payment_type=PaymentType.CREDIT,
            policy_id=sample_policy.id,
            success=True
        )
        db.session.add(payment)
        db.session.commit()
        return payment
