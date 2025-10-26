"""
Configuration settings for the data warehouse application
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent


class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database settings
    DATABASE_PATH = os.environ.get('DATABASE_PATH', BASE_DIR / 'data' / 'data_warehouse.db')
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DATABASE_PATH}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API settings
    API_TITLE = 'Data Warehouse API'
    API_VERSION = '1.0'
    API_DESCRIPTION = (
        'API for managing insurance data warehouse with users, quotes, '
        'policies, and payment transactions'
    )
    
    # Swagger settings
    SWAGGER_URL = '/swagger/'
    API_PREFIX = '/api/v1'
    
    # Backup settings
    BACKUP_DIR = os.environ.get('BACKUP_DIR', BASE_DIR / 'data' / 'backups')
    MAX_BACKUPS = int(os.environ.get('MAX_BACKUPS', '10'))
    
    # Pagination settings
    DEFAULT_PAGE_SIZE = int(os.environ.get('DEFAULT_PAGE_SIZE', '20'))
    MAX_PAGE_SIZE = int(os.environ.get('MAX_PAGE_SIZE', '100'))
    
    # OpenAI settings
    OPENAI_API_KEY = None  # Will be set dynamically via API


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    DATABASE_PATH = ':memory:'  # Use in-memory database for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or Config.SECRET_KEY


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
