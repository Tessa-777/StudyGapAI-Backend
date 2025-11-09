"""
Vercel serverless function adapter for Flask app.
This file is the entry point for Vercel serverless functions.

Vercel automatically detects Flask applications when an `app` instance
is exported from this file.
"""
import sys
from pathlib import Path

# Add the project root to the Python path
# This allows imports from the backend package
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
	sys.path.insert(0, str(project_root))

# Import the Flask app instance
# Vercel will automatically detect and serve this Flask app
from backend.app import app

# Export the app for Vercel
# Vercel's Python runtime automatically wraps Flask apps
__all__ = ['app']

