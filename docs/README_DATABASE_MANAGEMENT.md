# Database Management Guide

This guide explains how to safely manage database schema changes in the Data Warehouse project.

## Overview

The project uses SQLite with SQLAlchemy ORM. We provide two approaches for managing database changes:
- **Simple Backup & Recreate** (Recommended for development)
- **Flask-Migrate** (For production environments)

## File Structure

```
warehouse/
├── data_warehouse_models.py    # Database models/schema
├── create_data_warehouse.py    # Initial data generation
├── backup_db.py               # Backup utilities
├── recreate_db.py             # Schema recreation script
├── manage_db.py               # Migration management (optional)
└── db_backups/                # Backup storage directory
```

## Simple Approach: Backup & Recreate

### 1. Adding a New Column

**Step 1: Create Backup**
```bash
python backup_db.py backup
```

**Step 2: Modify Model**
Edit `data_warehouse_models.py`:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=True)  # NEW COLUMN
```

**Step 3: Recreate Database**
```bash
python recreate_db.py
```

### 2. Adding a New Table

**Step 1: Create Backup**
```bash
python backup_db.py backup
```

**Step 2: Add New Model**
Add to `data_warehouse_models.py`:

```python
class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User")
    street = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
```

**Step 3: Update Data Generation (Optional)**
Add to `create_data_warehouse.py`:

```python
def insert_address(user: User):
    address = Address()
    address.user_id = user.id
    address.user = user
    address.street = fake.street_address()
    address.city = fake.city()
    address.state = fake.state()
    address.zip_code = fake.zipcode()
    db.session.add(address)
    return address

# Add to main execution
addresses = [insert_address(user) for user in users]
db.session.commit()
```

**Step 4: Recreate Database**
```bash
python recreate_db.py
```

### 3. Modifying Existing Columns

**Step 1: Create Backup**
```bash
python backup_db.py backup
```

**Step 2: Modify Column Definition**
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)  # Changed from 80 to 120
```

**Step 3: Recreate Database**
```bash
python recreate_db.py
```

### 4. Adding Relationships

**Step 1: Create Backup**
```bash
python backup_db.py backup
```

**Step 2: Add Relationship**
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    # Add back-reference to quotes
    quotes = db.relationship("Quote", back_populates="user")

class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", back_populates="quotes")  # Updated
    # ... other fields
```

**Step 3: Recreate Database**
```bash
python recreate_db.py
```

### 5. Adding Indexes

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=True, index=True)  # Add index
    
    # Or create composite index
    __table_args__ = (
        db.Index('idx_user_name_email', 'name', 'email'),
    )
```

### 6. Adding Constraints

```python
class PaymentTransaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Decimal(10, 2), nullable=False)  # Add amount with precision
    payment_type = db.Column(db.Enum(PaymentType))
    policy_id = db.Column(db.Integer, db.ForeignKey("policy.id"), nullable=False)
    policy = db.relationship("Policy")
    success = db.Column(db.Boolean)
    
    # Add table constraints
    __table_args__ = (
        db.CheckConstraint('amount > 0', name='positive_amount'),
        db.UniqueConstraint('policy_id', 'time', name='unique_policy_payment_time'),
    )
```

## Advanced: Flask-Migrate Approach

### Setup (One Time)

```bash
# Set environment
export FLASK_APP=api.py

# Initialize migrations
python manage_db.py init-db
```

### Making Changes

**Step 1: Modify Models**
Edit `data_warehouse_models.py` with your changes.

**Step 2: Generate Migration**
```bash
python manage_db.py create-migration
# Enter descriptive message like "Add email to User"
```

**Step 3: Review Migration**
Check the generated file in `migrations/versions/` before applying.

**Step 4: Apply Migration**
```bash
python manage_db.py apply-migrations
```

### Migration Commands

```bash
python manage_db.py create-migration     # Create new migration
python manage_db.py apply-migrations     # Apply pending migrations
python manage_db.py rollback            # Rollback last migration
python manage_db.py migration-history   # Show migration history
python manage_db.py current-revision    # Show current revision
```

## Common Column Types

```python
# String fields
name = db.Column(db.String(80), nullable=False)
email = db.Column(db.String(120), nullable=True, unique=True)
description = db.Column(db.Text)  # For long text

# Numeric fields
age = db.Column(db.Integer)
price = db.Column(db.Decimal(10, 2))  # For money
rating = db.Column(db.Float)

# Date/Time fields
created_at = db.Column(db.DateTime, default=datetime.utcnow)
updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
birth_date = db.Column(db.Date)

# Boolean fields
is_active = db.Column(db.Boolean, default=True)
is_verified = db.Column(db.Boolean, default=False)

# JSON fields (SQLite 3.38+)
metadata = db.Column(db.JSON)

# Enum fields
status = db.Column(db.Enum(StatusEnum))
```

## Best Practices

1. **Always backup before changes**
2. **Use descriptive column names**
3. **Set appropriate nullable constraints**
4. **Add indexes for frequently queried columns**
5. **Use foreign keys for relationships**
6. **Consider data migration for existing data**
7. **Test changes with sample data**
8. **Document schema changes**

## Troubleshooting

### "Table already exists" Error
```bash
# Remove existing database and recreate
rm data_warehouse.db
python recreate_db.py
```

### "Column doesn't exist" Error
```bash
# Restore from backup and try again
python backup_db.py restore db_backups/your_backup.db
```

### Migration Conflicts
```bash
# Reset migrations (development only)
rm -rf migrations/
python manage_db.py init-db
```

## Testing Schema Changes

```python
# Test script example
from api import app, db
from data_warehouse_models import User

with app.app_context():
    # Test new column
    user = User(name="Test User", email="test@example.com")
    db.session.add(user)
    db.session.commit()
    print(f"Created user: {user.name} with email: {user.email}")
```
