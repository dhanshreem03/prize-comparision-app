"""
Configuration settings for the Prize Comparison App.
"""

import os
from datetime import timedelta

# Flask Configuration
DEBUG = os.environ.get('FLASK_DEBUG', True)
TESTING = os.environ.get('FLASK_TESTING', False)

# Database Configuration
SQLALCHEMY_DATABASE_URI = os.environ.get(
    'DATABASE_URL', 'sqlite:///prize_comparison.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Session Configuration
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# Scraper Configuration
SCRAPER_HEADLESS = True
SCRAPER_TIMEOUT = 60000  # milliseconds
SCREENSHOT_FOLDER = os.path.join(os.path.dirname(__file__), 'screenshots')

# Create screenshot folder if it doesn't exist
if not os.path.exists(SCREENSHOT_FOLDER):
    os.makedirs(SCREENSHOT_FOLDER)
