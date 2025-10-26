#!/usr/bin/env python3
"""
Seed the database with sample data for development and testing
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
import random

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import create_app
from app.models import db, User, Quote, Policy, PaymentTransaction, PaymentType


def seed_users(count=10):
    """Create sample users"""
    users = []
    names = [
        "John Doe", "Jane Smith", "Bob Johnson", "Alice Brown", "Charlie Wilson",
        "Diana Davis", "Eve Miller", "Frank Garcia", "Grace Lee", "Henry Taylor"
    ]
    
    for i in range(min(count, len(names))):
        user = User(
            name=names[i],
            email=f"{names[i].lower().replace(' ', '.')}@example.com"
        )
        users.append(user)
        db.session.add(user)
    
    db.session.commit()
    print(f"Created {len(users)} users")
    return users


def seed_quotes(users, quotes_per_user=2):
    """Create sample quotes"""
    quotes = []
    
    for user in users:
        for i in range(quotes_per_user):
            # Create quote with random creation time in the past 30 days
            create_time = datetime.utcnow() - timedelta(days=random.randint(1, 30))
            
            quote = Quote(
                user_id=user.id,
                create_time=create_time,
                bindable=random.choice([True, True, True, False])  # 75% bindable
            )
            
            # Some quotes are bound
            if quote.bindable and random.choice([True, False]):
                quote.bind_time = create_time + timedelta(hours=random.randint(1, 48))
            
            quotes.append(quote)
            db.session.add(quote)
    
    db.session.commit()
    print(f"Created {len(quotes)} quotes")
    return quotes


def seed_policies(quotes):
    """Create sample policies from bound quotes"""
    policies = []
    
    bound_quotes = [q for q in quotes if q.bind_time]
    
    for quote in bound_quotes:
        # 80% chance to create a policy from a bound quote
        if random.choice([True, True, True, True, False]):
            policy = Policy(
                user_id=quote.user_id,
                quote_id=quote.id
            )
            policies.append(policy)
            db.session.add(policy)
    
    db.session.commit()
    print(f"Created {len(policies)} policies")
    return policies


def seed_payments(policies, payments_per_policy=3):
    """Create sample payment transactions"""
    payments = []
    payment_types = list(PaymentType)
    
    for policy in policies:
        num_payments = random.randint(1, payments_per_policy)
        
        for i in range(num_payments):
            # Payment time after policy creation
            payment_time = datetime.utcnow() - timedelta(days=random.randint(0, 15))
            
            payment = PaymentTransaction(
                time=payment_time,
                payment_type=random.choice(payment_types),
                policy_id=policy.id,
                success=random.choice([True, True, True, False])  # 75% success rate
            )
            payments.append(payment)
            db.session.add(payment)
    
    db.session.commit()
    print(f"Created {len(payments)} payment transactions")
    return payments


def clear_all_data():
    """Clear all existing data"""
    PaymentTransaction.query.delete()
    Policy.query.delete()
    Quote.query.delete()
    User.query.delete()
    db.session.commit()
    print("Cleared all existing data")


def seed_database(clear_existing=False):
    """Seed the database with sample data"""
    if clear_existing:
        clear_all_data()
    
    print("Seeding database with sample data...")
    
    # Create sample data
    users = seed_users(10)
    quotes = seed_quotes(users, 2)
    policies = seed_policies(quotes)
    payments = seed_payments(policies, 3)
    
    print("\nDatabase seeding completed!")
    print(f"Summary:")
    print(f"  Users: {len(users)}")
    print(f"  Quotes: {len(quotes)}")
    print(f"  Policies: {len(policies)}")
    print(f"  Payments: {len(payments)}")


if __name__ == "__main__":
    app = create_app('development')
    
    with app.app_context():
        if len(sys.argv) > 1 and sys.argv[1] == "--clear":
            seed_database(clear_existing=True)
        else:
            seed_database(clear_existing=False)
