"""
Validation utility functions
"""
import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
    
    Returns:
        True if email is valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_name(name: str) -> bool:
    """
    Validate name format
    
    Args:
        name: Name to validate
    
    Returns:
        True if name is valid, False otherwise
    """
    if not name or not isinstance(name, str):
        return False
    
    # Name should be between 1 and 80 characters, contain only letters, spaces, hyphens, and apostrophes
    if len(name.strip()) < 1 or len(name) > 80:
        return False
    
    pattern = r"^[a-zA-Z\s\-']+$"
    return bool(re.match(pattern, name.strip()))


def sanitize_string(value: Optional[str], max_length: Optional[int] = None) -> Optional[str]:
    """
    Sanitize string input
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string or None
    """
    if not value:
        return None
    
    # Strip whitespace
    sanitized = value.strip()
    
    if not sanitized:
        return None
    
    # Truncate if necessary
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def validate_positive_integer(value: int) -> bool:
    """
    Validate that a value is a positive integer
    
    Args:
        value: Value to validate
    
    Returns:
        True if value is a positive integer, False otherwise
    """
    return isinstance(value, int) and value > 0


def validate_payment_type(payment_type: str) -> bool:
    """
    Validate payment type
    
    Args:
        payment_type: Payment type to validate
    
    Returns:
        True if payment type is valid, False otherwise
    """
    valid_types = {'CREDIT', 'DEBIT', 'PREPAID'}
    return payment_type in valid_types
