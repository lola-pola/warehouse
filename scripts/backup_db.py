#!/usr/bin/env python3
"""
Database backup and restore utility using the new app structure
"""
import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import from app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import config
from app.utils.database import backup_database, restore_database, cleanup_old_backups

def create_backup():
    """Create a timestamped backup of the database."""
    cfg = config['default']()
    
    try:
        backup_path = backup_database(
            source_path=cfg.DATABASE_PATH,
            backup_dir=cfg.BACKUP_DIR,
            max_backups=cfg.MAX_BACKUPS
        )
        print(f"Database backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Backup failed: {e}")
        return None

def restore_from_backup(backup_file):
    """Restore database from backup."""
    cfg = config['default']()
    
    try:
        success = restore_database(backup_file, cfg.DATABASE_PATH)
        if success:
            print(f"Database restored from: {backup_file}")
        else:
            print(f"Failed to restore from: {backup_file}")
    except Exception as e:
        print(f"Restore failed: {e}")

def list_backups():
    """List available backups."""
    cfg = config['default']()
    backup_dir = Path(cfg.BACKUP_DIR)
    
    if backup_dir.exists():
        backups = sorted(
            backup_dir.glob("data_warehouse_*.db"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )
        
        if backups:
            print("Available backups (newest first):")
            for i, backup in enumerate(backups, 1):
                print(f"{i}. {backup.name}")
            return [str(b) for b in backups]
        else:
            print("No backups found")
            return []
    else:
        print("Backup directory does not exist")
        return []

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python backup_db.py backup")
        print("  python backup_db.py restore <backup_file>")
        print("  python backup_db.py list")
    elif sys.argv[1] == "backup":
        create_backup()
    elif sys.argv[1] == "restore" and len(sys.argv) > 2:
        restore_from_backup(sys.argv[2])
    elif sys.argv[1] == "list":
        list_backups()
    else:
        print("Invalid command. Use 'backup', 'restore <file>', or 'list'")
