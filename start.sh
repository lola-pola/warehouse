#!/bin/bash
# Startup script for the warehouse application

# Set the Python path to include the current directory
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Run the application
python app.py
