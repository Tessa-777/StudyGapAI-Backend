#!/usr/bin/env python3
"""
Test script to verify real AI calls are being made
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Add project root to path (tests are in tests/ subdirectory)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.config import AppConfig
from backend.services.ai_enhanced import EnhancedAIService

print("=" * 60)
print("Testing Real AI Call")
print("=" * 60)

# Initialize AI service
api_key = AppConfig.GOOGLE_API_KEY
model_name = AppConfig.AI_MODEL_NAME
mock_mode = AppConfig.AI_MOCK

print(f"\nConfiguration:")
print(f"  API Key: {'SET' if api_key else 'NOT SET'}")
print(f"  Model: {model_name}")
print(f"  Mock Mode: {mock_mode}")

ai_service = EnhancedAIService(api_key, model_name, mock_mode)

print(f"\nAI Service State:")
print(f"  mock: {ai_service.mock}")
print(f"  model_name: {ai_service.model_name}")
print(f"  api_key: {'SET' if ai_service.api_key else 'NOT SET'}")

if ai_service.mock:
    print("\n❌ PROBLEM: AI Service is in MOCK mode!")
    print("   This means no real API calls will be made.")
    sys.exit(1)

# Test with a small quiz
test_quiz_data = {
    "subject": "Mathematics",
    "total_questions": 2,
    "time_taken": 5.0,
    "questions_list": [
        {
            "id": 1,
            "topic": "Algebra",
            "student_answer": "A",
            "correct_answer": "B",
            "is_correct": False,
            "confidence": 2,
            "explanation": "Test explanation",
            "time_spent_seconds": 30
        },
        {
            "id": 2,
            "topic": "Geometry",
            "student_answer": "C",
            "correct_answer": "C",
            "is_correct": False,
            "confidence": 1,
            "explanation": "Test explanation",
            "time_spent_seconds": 1000
        }
    ]
}

print(f"\n🧪 Testing AI Analysis (this will make a real API call)...")
print("   Note: This will use your Gemini API quota!")

try:
    result = ai_service.analyze_diagnostic(test_quiz_data)
    print("\n✅ SUCCESS: AI analysis completed!")
    print(f"   Result keys: {list(result.keys())}")
    print(f"   Overall performance: {result.get('overall_performance', {}).get('accuracy', 'N/A')}%")
    print(f"   Topics analyzed: {len(result.get('topic_breakdown', []))}")
    print("\n✅ Real AI is working! Check your Gemini API usage to confirm.")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print(f"   Error type: {type(e).__name__}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)

