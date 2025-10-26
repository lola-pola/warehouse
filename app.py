"""
Main application entry point
"""
import os
from app import create_app

# Get configuration from environment variable
config_name = os.environ.get('FLASK_ENV', 'development')

# Create Flask application
app = create_app(config_name)

if __name__ == "__main__":
    # Run the application
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 25000))
    debug = config_name == 'development'
    app.run(host=host, port=port, debug=debug)