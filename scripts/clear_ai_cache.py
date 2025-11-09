#!/usr/bin/env python3
"""
Script to clear AI cache - useful for testing real AI calls
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add project root to path (scripts are in scripts/ subdirectory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask
from backend.app import create_app

app = create_app()

with app.app_context():
    cache = app.extensions.get("cache_instance")
    if cache:
        cache.clear()
        print("✅ AI cache cleared!")
        print("   Next quiz submission will make a fresh API call.")
    else:
        print("⚠️ No cache instance found (cache might not be enabled)")

print("\n💡 Tip: Restart Flask after clearing cache to ensure fresh start.")

