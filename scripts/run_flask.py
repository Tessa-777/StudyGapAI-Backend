#!/usr/bin/env python
"""
Run Flask development server with proper logging configuration.

This script ensures logs are visible in the terminal.
Run from project root: python scripts/run_flask.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path (scripts are in scripts/ subdirectory)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables from project root
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()

# Set Flask environment to development if not set
if not os.getenv("FLASK_ENV"):
    os.environ["FLASK_ENV"] = "development"

# Import Flask app
from backend.app import app

if __name__ == "__main__":
    # Get host and port from environment or use defaults
    host = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_RUN_PORT", 5000))
    
    print("=" * 60)
    print("Starting Flask development server...")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Debug mode: {app.config.get('DEBUG', False)}")
    print("=" * 60)
    print("Backend logs will appear below:")
    print("=" * 60)
    print()
    
    # Run Flask app
    app.run(host=host, port=port, debug=True, use_reloader=True)

