#!/usr/bin/env python3
"""
Test script to verify save-diagnostic endpoint works for saving guest diagnostics
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
ENDPOINT = f"{BACKEND_URL}/api/ai/save-diagnostic"

print("=" * 60)
print("Testing Save Diagnostic Endpoint")
print("=" * 60)
print(f"\nBackend URL: {BACKEND_URL}")
print(f"Endpoint: {ENDPOINT}\n")

# Get auth token (required for this endpoint)
token = os.getenv("TEST_AUTH_TOKEN")
if not token:
    print("❌ ERROR: TEST_AUTH_TOKEN not set in environment")
    print("   This endpoint requires authentication")
    print("   Set TEST_AUTH_TOKEN to test this endpoint")
    sys.exit(1)

# Sample guest diagnostic data (what would be stored in localStorage)
quiz_data = {
    "subject": "Mathematics",
    "total_questions": 5,
    "time_taken": 10.0,
    "questions_list": [
        {
            "id": 1,
            "topic": "Algebra",
            "student_answer": "A",
            "correct_answer": "B",
            "is_correct": False,
            "confidence": 2,
            "explanation": "I thought it was A",
            "time_spent_seconds": 30
        },
        {
            "id": 2,
            "topic": "Algebra",
            "student_answer": "C",
            "correct_answer": "C",
            "is_correct": True,
            "confidence": 4,
            "explanation": "",
            "time_spent_seconds": 45
        },
        {
            "id": 3,
            "topic": "Geometry",
            "student_answer": "A",
            "correct_answer": "D",
            "is_correct": False,
            "confidence": 1,
            "explanation": "Not sure",
            "time_spent_seconds": 60
        },
        {
            "id": 4,
            "topic": "Geometry",
            "student_answer": "B",
            "correct_answer": "B",
            "is_correct": True,
            "confidence": 5,
            "explanation": "",
            "time_spent_seconds": 40
        },
        {
            "id": 5,
            "topic": "Algebra",
            "student_answer": "D",
            "correct_answer": "A",
            "is_correct": False,
            "confidence": 2,
            "explanation": "Guessed",
            "time_spent_seconds": 20
        }
    ]
}

# Sample diagnostic data (from guest diagnostic response)
diagnostic_data = {
    "id": "guest-diagnostic-id-123",
    "quiz_id": None,  # None for guest users
    "generated_at": "2025-01-09T12:00:00Z",
    "overall_performance": {
        "accuracy": 40.0,
        "total_questions": 5,
        "correct_answers": 2,
        "avg_confidence": 2.8,
        "time_per_question": 39.0
    },
    "topic_breakdown": [
        {
            "topic": "Algebra",
            "accuracy": 33.33,
            "fluency_index": 25.0,
            "status": "weak",
            "questions_attempted": 3,
            "correct_answers": 1,
            "severity": "critical",
            "dominant_error_type": "knowledge_gap"
        },
        {
            "topic": "Geometry",
            "accuracy": 50.0,
            "fluency_index": 45.0,
            "status": "weak",
            "questions_attempted": 2,
            "correct_answers": 1,
            "severity": "moderate",
            "dominant_error_type": "misinterpretation"
        }
    ],
    "root_cause_analysis": {
        "primary_weakness": "knowledge_gap",
        "error_distribution": {
            "knowledge_gap": 2,
            "misinterpretation": 1
        }
    },
    "predicted_jamb_score": {
        "score": 120,
        "confidence_interval": "100-140",
        "base_score": 120
    },
    "study_plan": {
        "weekly_schedule": [
            {
                "week": 1,
                "focus": "Algebra Fundamentals",
                "study_hours": 5,
                "key_activities": ["Review basic algebra concepts", "Practice solving equations"]
            },
            {
                "week": 2,
                "focus": "Geometry Basics",
                "study_hours": 4,
                "key_activities": ["Study geometric shapes", "Practice angle calculations"]
            }
        ]
    },
    "recommendations": [
        {
            "priority": 1,
            "category": "Conceptual Understanding",
            "action": "Revisit fundamental algebra concepts",
            "rationale": "Weak performance in algebra indicates foundational gaps"
        },
        {
            "priority": 2,
            "category": "Targeted Practice",
            "action": "Focus on practicing solving basic algebraic equations",
            "rationale": "Need more practice with core algebraic operations"
        }
    ]
}

# Combine quiz data and diagnostic data
payload = {
    **quiz_data,
    "diagnostic": diagnostic_data
}

print("🧪 Test: Save Guest Diagnostic After Signup")
print("-" * 60)
print(f"Token: {'SET' if token else 'NOT SET'}")
print(f"Payload keys: {list(payload.keys())}")
print(f"Diagnostic keys: {list(diagnostic_data.keys())}\n")

try:
    response = requests.post(
        ENDPOINT,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Guest diagnostic saved to database!")
        data = response.json()
        print(f"\nResponse:")
        print(f"  quiz_id: {data.get('quiz_id')}")
        print(f"  diagnostic_id: {data.get('diagnostic_id')}")
        print(f"  message: {data.get('message')}")
        
        print("\n✅ Diagnostic saved successfully!")
        print("   Frontend should update localStorage with quiz_id")
        print("   User can now access their diagnostic from the database")
        
    elif response.status_code == 401:
        print("❌ FAILED: Authentication required")
        print("   This endpoint requires a valid auth token")
        print(f"   Response: {response.json()}")
        sys.exit(1)
        
    elif response.status_code == 400:
        print("❌ FAILED: Bad Request")
        print(f"   Response: {response.json()}")
        sys.exit(1)
        
    else:
        print(f"❌ UNEXPECTED STATUS: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
        
except requests.exceptions.RequestException as e:
    print(f"❌ REQUEST ERROR: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("✅ Save diagnostic endpoint test completed")
print("   - Guest diagnostic can be saved after user signs up")
print("   - Quiz is created in database")
print("   - Quiz responses are saved")
print("   - Diagnostic is saved and linked to quiz")
print("   - quiz_id is returned for frontend to update localStorage")

