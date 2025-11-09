#!/usr/bin/env python3
"""
Test script to diagnose AI configuration issues
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to Python path (tests are in tests/ subdirectory)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables from project root
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
else:
    load_dotenv()

print("=" * 60)
print("AI Configuration Diagnostic")
print("=" * 60)

# Check environment variables
print("\n1. Environment Variables:")
print(f"   GOOGLE_API_KEY: {'SET' if os.getenv('GOOGLE_API_KEY') else 'NOT SET'}")
print(f"   GEMINI_API_KEY: {'SET' if os.getenv('GEMINI_API_KEY') else 'NOT SET'}")
print(f"   AI_MOCK: {os.getenv('AI_MOCK', 'NOT SET')}")
print(f"   AI_MODEL_NAME: {os.getenv('AI_MODEL_NAME', 'NOT SET')}")
print(f"   FLASK_DEBUG: {os.getenv('FLASK_DEBUG', 'NOT SET')}")
print(f"   TESTING: {os.getenv('TESTING', 'NOT SET')}")

# Check API key
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    print(f"\n   API Key (first 10 chars): {api_key[:10]}...")
    print(f"   API Key length: {len(api_key)}")
else:
    print("\n   ❌ API KEY IS MISSING!")

# Check AI_MOCK parsing
ai_mock_env = os.getenv("AI_MOCK", "true")
ai_mock_bool = ai_mock_env.lower() == "true"
print(f"\n2. AI_MOCK Parsing:")
print(f"   Raw value: '{ai_mock_env}'")
print(f"   Parsed as boolean: {ai_mock_bool}")
print(f"   Expected: False (to use real AI)")
print(f"   Actual: {ai_mock_bool} {'✅' if not ai_mock_bool else '❌ WRONG!'}")

# Check how config.py will parse it
print(f"\n3. Config.py Parsing:")
from backend.config import AppConfig
print(f"   AppConfig.AI_MOCK: {AppConfig.AI_MOCK}")
print(f"   AppConfig.GOOGLE_API_KEY: {'SET' if AppConfig.GOOGLE_API_KEY else 'NOT SET'}")
print(f"   AppConfig.AI_MODEL_NAME: {AppConfig.AI_MODEL_NAME}")

# Check EnhancedAIService initialization
print(f"\n4. EnhancedAIService Initialization:")
mock_param = AppConfig.AI_MOCK
api_key_param = AppConfig.GOOGLE_API_KEY
# This is the logic from EnhancedAIService.__init__
final_mock = mock_param or not api_key_param
print(f"   mock parameter: {mock_param}")
print(f"   api_key parameter: {'SET' if api_key_param else 'NOT SET'}")
print(f"   Final mock mode: {final_mock} {'❌ USING MOCK!' if final_mock else '✅ USING REAL AI'}")
print(f"   Logic: mock or not api_key = {mock_param} or {not api_key_param} = {final_mock}")

# Diagnosis
print(f"\n5. Diagnosis:")
issues = []
if not api_key:
    issues.append("❌ API key is missing (GOOGLE_API_KEY or GEMINI_API_KEY)")
if ai_mock_bool:
    issues.append("❌ AI_MOCK is set to 'true' (should be 'false')")
if final_mock:
    if not api_key:
        issues.append("❌ EnhancedAIService will use mock because API key is missing")
    elif mock_param:
        issues.append("❌ EnhancedAIService will use mock because AI_MOCK=True")

if issues:
    print("   Issues found:")
    for issue in issues:
        print(f"   {issue}")
else:
    print("   ✅ No issues found - AI should be working!")

print("\n" + "=" * 60)
print("Recommendations:")
print("=" * 60)

if not api_key:
    print("1. Set GOOGLE_API_KEY or GEMINI_API_KEY in your .env file")
if ai_mock_bool:
    print("2. Set AI_MOCK=false in your .env file (not 'False' or '0', but 'false')")
if final_mock and api_key:
    print("3. Restart Flask after changing environment variables")
    
print("\n" + "=" * 60)

