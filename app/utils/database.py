"""
Database utility functions
"""
import os
import shutil
from datetime import datetime
from pathlib import Path
from app.models import db


def backup_database(source_path: str, backup_dir: str, max_backups: int = 10) -> str:
    """
    Create a backup of the database file
    
    Args:
        source_path: Path to the source database file
        backup_dir: Directory to store backups
        max_backups: Maximum number of backups to keep
    
    Returns:
        Path to the created backup file
    """
    # Create backup directory if it doesn't exist
    backup_path = Path(backup_dir)
    backup_path.mkdir(parents=True, exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"data_warehouse_{timestamp}.db"
    backup_file_path = backup_path / backup_filename
    
    # Copy the database file
    shutil.copy2(source_path, backup_file_path)
    
    # Clean up old backups
    cleanup_old_backups(backup_dir, max_backups)
    
    return str(backup_file_path)


def cleanup_old_backups(backup_dir: str, max_backups: int):
    """
    Remove old backup files, keeping only the most recent ones
    
    Args:
        backup_dir: Directory containing backup files
        max_backups: Maximum number of backups to keep
    """
    backup_path = Path(backup_dir)
    if not backup_path.exists():
        return
    
    # Get all backup files sorted by modification time (newest first)
    backup_files = sorted(
        backup_path.glob("data_warehouse_*.db"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    
    # Remove excess backups
    for backup_file in backup_files[max_backups:]:
        backup_file.unlink()


def restore_database(backup_path: str, target_path: str) -> bool:
    """
    Restore database from a backup file
    
    Args:
        backup_path: Path to the backup file
        target_path: Path where to restore the database
    
    Returns:
        True if restoration was successful, False otherwise
    """
    try:
        # Create target directory if it doesn't exist
        target_dir = Path(target_path).parent
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy backup to target location
        shutil.copy2(backup_path, target_path)
        return True
    except Exception:
        return False


def initialize_database():
    """Initialize the database with all tables"""
    db.create_all()


def drop_all_tables():
    """Drop all database tables"""
    db.drop_all()


def recreate_database():
    """Drop all tables and recreate them"""
    drop_all_tables()
    initialize_database()
