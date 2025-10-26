#!/usr/bin/env python3
"""
Recreate database with new schema and regenerate test data
"""
import os
from api import app, db
from create_data_warehouse import *

def recreate_database():
    """Drop existing database, create new schema, and populate with test data."""
    
    # Backup first
    print("Creating backup...")
    os.system("python backup_db.py backup")
    
    with app.app_context():
        print("Dropping existing tables...")
        db.drop_all()
        
        print("Creating new tables...")
        db.create_all()
        
        print("Generating test data...")
        # Reuse the data generation logic from create_data_warehouse.py
        users = [insert_user() for i in range(NUM_USERS)]
        db.session.commit()

        quotes = [insert_quote(random.choice(users)) for i in range(NUM_QUOTES)]
        db.session.commit()

        policies = [insert_policy(random.choice(quotes)) for i in range(NUM_POLICIES)]
        db.session.commit()

        payment_transactions = [insert_payment_transaction(policy) for policy in policies]
        db.session.commit()
        
        print("Database recreated successfully!")

if __name__ == "__main__":
    recreate_database()
