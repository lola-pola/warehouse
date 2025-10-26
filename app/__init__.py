"""
Flask application factory
"""
from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate

from app.config import config
from app.models import db
from app.api import (
    create_api_schemas,
    create_user_namespace,
    create_quote_namespace,
    create_policy_namespace,
    create_payment_namespace,
    create_analytics_namespace,
    create_openai_namespace,
    create_feature_store_namespace
)


def create_app(config_name='default'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration to use ('development', 'testing', 'production')
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize Flask-RESTX API
    api = Api(
        app,
        version=app.config['API_VERSION'],
        title=app.config['API_TITLE'],
        description=app.config['API_DESCRIPTION'],
        doc=app.config['SWAGGER_URL'],
        prefix=app.config['API_PREFIX']
    )
    
    # Create API schemas
    schemas = create_api_schemas(api)
    
    # Create and register namespaces
    users_ns = create_user_namespace(api, schemas)
    quotes_ns = create_quote_namespace(api, schemas)
    policies_ns = create_policy_namespace(api, schemas)
    payments_ns = create_payment_namespace(api, schemas)
    analytics_ns = create_analytics_namespace(api, schemas)
    openai_ns = create_openai_namespace(api, schemas)
    features_ns = create_feature_store_namespace(api, schemas)
    
    # Add namespaces to API
    api.add_namespace(users_ns)
    api.add_namespace(quotes_ns)
    api.add_namespace(policies_ns)
    api.add_namespace(payments_ns)
    api.add_namespace(analytics_ns)
    api.add_namespace(openai_ns)
    api.add_namespace(features_ns)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
