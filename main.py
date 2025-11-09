"""
Main entry point for Replit deployment.
This file runs the Flask application on Replit.
"""
import os
from backend.app import app

if __name__ == "__main__":
    # Replit automatically provides PORT environment variable
    # Use 0.0.0.0 to accept connections from outside the repl
    port = int(os.environ.get("PORT", 5000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # Determine if we're in production (Replit) or development
    # Replit sets FLASK_ENV=production in secrets
    is_production = os.environ.get("FLASK_ENV") == "production"
    
    # Run the Flask app
    # Debug mode: False in production (Replit), True in development
    # use_reloader: False in production to avoid issues with Replit
    app.run(
        host=host, 
        port=port, 
        debug=not is_production,
        use_reloader=not is_production
    )

