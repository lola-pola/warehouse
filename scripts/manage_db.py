#!/usr/bin/env python3
"""
Database migration management script
"""
import os
import sys
import subprocess
from flask.cli import FlaskGroup
from api import app, db

cli = FlaskGroup(app)

def run_flask_command(command):
    """Run a Flask command using subprocess to ensure proper environment."""
    env = os.environ.copy()
    env['FLASK_APP'] = 'api.py'
    
    # Use the correct Python path from pyenv
    python_path = '/Users/elhayef/.pyenv/versions/3.12.2/bin/python'
    
    try:
        result = subprocess.run(
            [python_path, '-m', 'flask'] + command.split(),
            capture_output=True,
            text=True,
            env=env,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}", file=sys.stderr)
        return False

@cli.command()
def init_db():
    """Initialize the database with migrations."""
    print("Initializing migration repository...")
    if not run_flask_command('db init'):
        print("Failed to initialize migration repository")
        return
    
    print("Creating initial migration...")
    if not run_flask_command('db migrate -m Initial_migration'):
        print("Failed to create initial migration")
        return
    
    print("Applying migration...")
    if not run_flask_command('db upgrade'):
        print("Failed to apply migration")
        return
    
    print("Database initialized successfully!")

@cli.command()
def create_migration():
    """Create a new migration after model changes."""
    message = input("Enter migration message: ")
    if not message:
        message = "Auto-generated migration"
    print(f"Creating migration: {message}")
    # Replace spaces with underscores to avoid command parsing issues
    safe_message = message.replace(' ', '_')
    if run_flask_command(f'db migrate -m {safe_message}'):
        print("Migration created! Review it before applying.")
    else:
        print("Failed to create migration")

@cli.command()
def apply_migrations():
    """Apply pending migrations."""
    print("Applying migrations...")
    if run_flask_command('db upgrade'):
        print("Migrations applied successfully!")
    else:
        print("Failed to apply migrations")

@cli.command()
def rollback():
    """Rollback the last migration."""
    print("Rolling back last migration...")
    if run_flask_command('db downgrade'):
        print("Rollback completed!")
    else:
        print("Failed to rollback migration")

@cli.command()
def migration_history():
    """Show migration history."""
    run_flask_command('db history')

@cli.command()
def current_revision():
    """Show current database revision."""
    run_flask_command('db current')

if __name__ == '__main__':
    cli()
