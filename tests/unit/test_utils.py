"""
Unit tests for utility functions
"""
import pytest
import tempfile
import os
from pathlib import Path
from app.utils.validators import (
    validate_email, validate_name, sanitize_string,
    validate_positive_integer, validate_payment_type
)
from app.utils.database import backup_database, cleanup_old_backups, restore_database


class TestValidators:
    """Test validation utility functions"""
    
    def test_validate_email_valid(self):
        """Test valid email addresses"""
        valid_emails = [
            'test@example.com',
            'user.name@domain.co.uk',
            'user+tag@example.org',
            'user123@test-domain.com'
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Test invalid email addresses"""
        invalid_emails = [
            'invalid-email',
            '@example.com',
            'user@',
            'user@.com',
            'user space@example.com',
            '',
            None
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False
    
    def test_validate_name_valid(self):
        """Test valid names"""
        valid_names = [
            'John Doe',
            'Mary-Jane Smith',
            "O'Connor",
            'Jean-Pierre',
            'A'  # Single character
        ]
        
        for name in valid_names:
            assert validate_name(name) is True
    
    def test_validate_name_invalid(self):
        """Test invalid names"""
        invalid_names = [
            '',
            '   ',  # Only whitespace
            'John123',  # Contains numbers
            'John@Doe',  # Contains special characters
            'A' * 81,  # Too long
            None,
            123  # Not a string
        ]
        
        for name in invalid_names:
            assert validate_name(name) is False
    
    def test_sanitize_string(self):
        """Test string sanitization"""
        assert sanitize_string('  hello  ') == 'hello'
        assert sanitize_string('') is None
        assert sanitize_string('   ') is None
        assert sanitize_string(None) is None
        assert sanitize_string('hello world', max_length=5) == 'hello'
    
    def test_validate_positive_integer(self):
        """Test positive integer validation"""
        assert validate_positive_integer(1) is True
        assert validate_positive_integer(100) is True
        assert validate_positive_integer(0) is False
        assert validate_positive_integer(-1) is False
        assert validate_positive_integer('1') is False
        assert validate_positive_integer(1.5) is False
    
    def test_validate_payment_type(self):
        """Test payment type validation"""
        assert validate_payment_type('CREDIT') is True
        assert validate_payment_type('DEBIT') is True
        assert validate_payment_type('PREPAID') is True
        assert validate_payment_type('INVALID') is False
        assert validate_payment_type('credit') is False  # Case sensitive
        assert validate_payment_type('') is False


class TestDatabaseUtils:
    """Test database utility functions"""
    
    def test_backup_database(self):
        """Test database backup functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a dummy database file
            db_file = Path(temp_dir) / 'test.db'
            db_file.write_text('dummy database content')
            
            backup_dir = Path(temp_dir) / 'backups'
            
            # Create backup
            backup_path = backup_database(str(db_file), str(backup_dir), max_backups=5)
            
            # Verify backup was created
            assert Path(backup_path).exists()
            assert Path(backup_path).read_text() == 'dummy database content'
            assert 'test_' in Path(backup_path).name
    
    def test_cleanup_old_backups(self):
        """Test cleanup of old backup files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_dir = Path(temp_dir)
            
            # Create multiple backup files
            for i in range(5):
                backup_file = backup_dir / f'data_warehouse_202301{i:02d}_120000.db'
                backup_file.write_text(f'backup {i}')
            
            # Cleanup keeping only 3 backups
            cleanup_old_backups(str(backup_dir), max_backups=3)
            
            # Count remaining backups
            remaining_backups = list(backup_dir.glob('data_warehouse_*.db'))
            assert len(remaining_backups) == 3
    
    def test_restore_database(self):
        """Test database restoration"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create backup file
            backup_file = Path(temp_dir) / 'backup.db'
            backup_file.write_text('backup content')
            
            # Create target path
            target_file = Path(temp_dir) / 'restored.db'
            
            # Restore database
            success = restore_database(str(backup_file), str(target_file))
            
            assert success is True
            assert target_file.exists()
            assert target_file.read_text() == 'backup content'
    
    def test_restore_nonexistent_backup(self):
        """Test restoring from non-existent backup"""
        with tempfile.TemporaryDirectory() as temp_dir:
            backup_file = Path(temp_dir) / 'nonexistent.db'
            target_file = Path(temp_dir) / 'target.db'
            
            success = restore_database(str(backup_file), str(target_file))
            assert success is False
