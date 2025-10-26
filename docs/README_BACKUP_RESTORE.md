# Database Backup & Restore Guide

This guide covers all backup and restore operations for the Data Warehouse project.

## Quick Reference

```bash
# Create backup
python backup_db.py backup

# List backups
python backup_db.py list

# Restore from backup
python backup_db.py restore db_backups/backup_file.db

# Recreate database (with backup)
python recreate_db.py
```

## Backup System Overview

The backup system automatically creates timestamped copies of your SQLite database in the `db_backups/` directory.

### Backup File Naming
```
data_warehouse_YYYYMMDD_HHMMSS.db
Example: data_warehouse_20241026_143022.db
```

## Backup Operations

### 1. Manual Backup

Create an immediate backup of your current database:

```bash
python backup_db.py backup
```

**Output:**
```
Database backed up to: db_backups/data_warehouse_20241026_143022.db
```

**When to use:**
- Before making schema changes
- Before running data migrations
- Before testing new features
- At the end of development sessions

### 2. Automatic Backup

The `recreate_db.py` script automatically creates a backup before recreating the database:

```bash
python recreate_db.py
```

**Output:**
```
Creating backup...
Database backed up to: db_backups/data_warehouse_20241026_143045.db
Dropping existing tables...
Creating new tables...
Generating test data...
Database recreated successfully!
```

## Restore Operations

### 1. List Available Backups

See all available backup files:

```bash
python backup_db.py list
```

**Output:**
```
Available backups:
1. data_warehouse_20241026_143045.db
2. data_warehouse_20241026_143022.db
3. data_warehouse_20241026_142815.db
```

### 2. Restore from Specific Backup

Replace your current database with a backup:

```bash
python backup_db.py restore db_backups/data_warehouse_20241026_143022.db
```

**Output:**
```
Database restored from: db_backups/data_warehouse_20241026_143022.db
```

### 3. Interactive Restore

For easier restore, you can modify the backup script to be interactive:

```python
# Add this to backup_db.py for interactive restore
def interactive_restore():
    backups = list_backups()
    if not backups:
        return
    
    try:
        choice = int(input("Enter backup number to restore: ")) - 1
        if 0 <= choice < len(backups):
            backup_file = f"{BACKUP_DIR}/{backups[choice]}"
            restore_database(backup_file)
        else:
            print("Invalid choice")
    except ValueError:
        print("Please enter a valid number")
```

## Backup Strategies

### 1. Development Workflow

```bash
# Start of day - create checkpoint
python backup_db.py backup

# Before major changes
python backup_db.py backup

# After successful changes
python backup_db.py backup

# End of day - final backup
python backup_db.py backup
```

### 2. Feature Development

```bash
# Before starting new feature
python backup_db.py backup

# After completing feature
python backup_db.py backup

# Before merging to main branch
python backup_db.py backup
```

### 3. Schema Changes

```bash
# Before schema change
python backup_db.py backup

# Make changes to data_warehouse_models.py
# Then recreate (which auto-backs up)
python recreate_db.py

# If problems occur, restore
python backup_db.py restore db_backups/your_backup.db
```

## Advanced Backup Management

### 1. Backup with Custom Names

Modify `backup_db.py` to support custom names:

```python
def backup_database_with_name(custom_name=None):
    """Create a backup with custom name."""
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    
    if os.path.exists(DB_FILE):
        if custom_name:
            backup_file = f"{BACKUP_DIR}/data_warehouse_{custom_name}.db"
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"{BACKUP_DIR}/data_warehouse_{timestamp}.db"
        
        shutil.copy2(DB_FILE, backup_file)
        print(f"Database backed up to: {backup_file}")
        return backup_file
```

Usage:
```bash
python -c "from backup_db import backup_database_with_name; backup_database_with_name('before_user_email_feature')"
```

### 2. Cleanup Old Backups

Add to `backup_db.py`:

```python
def cleanup_old_backups(keep_count=10):
    """Keep only the most recent N backups."""
    if os.path.exists(BACKUP_DIR):
        backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
        backups.sort(reverse=True)  # Most recent first
        
        if len(backups) > keep_count:
            for old_backup in backups[keep_count:]:
                old_path = os.path.join(BACKUP_DIR, old_backup)
                os.remove(old_path)
                print(f"Removed old backup: {old_backup}")
            
            print(f"Kept {keep_count} most recent backups")
```

### 3. Backup Verification

Add to `backup_db.py`:

```python
def verify_backup(backup_file):
    """Verify backup file integrity."""
    import sqlite3
    
    try:
        conn = sqlite3.connect(backup_file)
        cursor = conn.cursor()
        
        # Check if main tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        expected_tables = ['user', 'quote', 'policy', 'paymenttransaction']
        found_tables = [table[0] for table in tables]
        
        for expected in expected_tables:
            if expected not in found_tables:
                print(f"Warning: Table '{expected}' not found in backup")
                return False
        
        conn.close()
        print(f"Backup verification successful: {backup_file}")
        return True
        
    except Exception as e:
        print(f"Backup verification failed: {e}")
        return False
```

## Emergency Procedures

### 1. Database Corruption

If your database becomes corrupted:

```bash
# Step 1: Try to backup current state (might fail)
python backup_db.py backup

# Step 2: Restore from most recent backup
python backup_db.py list
python backup_db.py restore db_backups/most_recent_backup.db

# Step 3: If no backups work, recreate from scratch
python recreate_db.py
```

### 2. Accidental Data Loss

```bash
# Immediately restore from backup before the incident
python backup_db.py list
python backup_db.py restore db_backups/backup_before_incident.db
```

### 3. Schema Migration Gone Wrong

```bash
# Restore to state before migration
python backup_db.py restore db_backups/before_migration.db

# Fix the schema changes
# Then try again
python recreate_db.py
```

## Backup Best Practices

### 1. Frequency
- **Before any schema changes**
- **Before major data operations**
- **At least daily during active development**
- **Before deploying to production**

### 2. Naming Conventions
- Use descriptive names for important milestones
- Include date/time for regular backups
- Tag backups before major features

### 3. Storage
- Keep backups in version control for critical milestones
- Store backups outside project directory for safety
- Consider cloud storage for important backups

### 4. Testing
- Regularly test restore procedures
- Verify backup integrity
- Document restore procedures

## Automation Scripts

### Daily Backup Script

Create `daily_backup.sh`:

```bash
#!/bin/bash
cd /path/to/warehouse
python backup_db.py backup
python -c "from backup_db import cleanup_old_backups; cleanup_old_backups(30)"
echo "Daily backup completed: $(date)"
```

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
cd /path/to/warehouse
python backup_db.py backup
echo "Pre-commit backup created"
```

## Troubleshooting

### "No database file found"
```bash
# Create new database
python recreate_db.py
```

### "Backup file not found"
```bash
# Check backup directory
ls -la db_backups/
# Use correct path
python backup_db.py restore db_backups/correct_filename.db
```

### "Permission denied"
```bash
# Check file permissions
chmod 644 db_backups/*.db
chmod 755 backup_db.py
```

### "Database locked"
```bash
# Stop any running applications using the database
# Then try backup/restore again
```

## Monitoring Backup Health

Create `check_backups.py`:

```python
#!/usr/bin/env python3
import os
from datetime import datetime, timedelta
from backup_db import BACKUP_DIR, verify_backup

def check_backup_health():
    """Check backup directory health."""
    if not os.path.exists(BACKUP_DIR):
        print("❌ No backup directory found")
        return
    
    backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.db')]
    if not backups:
        print("❌ No backups found")
        return
    
    backups.sort(reverse=True)
    latest_backup = backups[0]
    
    # Check if latest backup is recent (within 24 hours)
    backup_path = os.path.join(BACKUP_DIR, latest_backup)
    backup_time = datetime.fromtimestamp(os.path.getmtime(backup_path))
    
    if datetime.now() - backup_time > timedelta(days=1):
        print(f"⚠️  Latest backup is old: {latest_backup} ({backup_time})")
    else:
        print(f"✅ Recent backup found: {latest_backup}")
    
    # Verify latest backup
    if verify_backup(backup_path):
        print("✅ Latest backup is valid")
    else:
        print("❌ Latest backup is corrupted")
    
    print(f"📊 Total backups: {len(backups)}")

if __name__ == "__main__":
    check_backup_health()
```

Run health check:
```bash
python check_backups.py
```
