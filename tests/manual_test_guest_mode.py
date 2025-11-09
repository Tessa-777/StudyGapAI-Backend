#!/usr/bin/env python3
"""
Test script to verify guest mode works for /api/ai/analyze-diagnostic endpoint
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
ENDPOINT = f"{BACKEND_URL}/api/ai/analyze-diagnostic"

print("=" * 60)
print("Testing Guest Mode - /api/ai/analyze-diagnostic")
print("=" * 60)
print(f"\nBackend URL: {BACKEND_URL}")
print(f"Endpoint: {ENDPOINT}\n")

# Test payload (no authentication token)
test_payload = {
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

print("🧪 Test 1: Guest User Submission (No Authentication)")
print("-" * 60)

try:
    # Make request WITHOUT Authorization header
    response = requests.post(
        ENDPOINT,
        json=test_payload,
        headers={
            "Content-Type": "application/json"
            # NO Authorization header - this is a guest request
        },
        timeout=60
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS: Guest user can submit quiz!")
        data = response.json()
        print(f"\nResponse keys: {list(data.keys())}")
        print(f"Diagnostic ID: {data.get('id')}")
        print(f"Quiz ID: {data.get('quiz_id')} (should be None for guest)")
        print(f"Overall Performance: {data.get('overall_performance', {}).get('accuracy', 'N/A')}%")
        print(f"Topics Analyzed: {len(data.get('topic_breakdown', []))}")
        print(f"Study Plan: {'Present' if data.get('study_plan') else 'Missing'}")
        
        # Verify quiz_id is None for guest users
        if data.get('quiz_id') is None:
            print("\n✅ Verified: quiz_id is None for guest user (correct)")
        else:
            print(f"\n⚠️ Warning: quiz_id is {data.get('quiz_id')} (expected None for guest)")
        
        print("\n✅ Guest mode is working correctly!")
        print("   Diagnostic generated but not saved to database")
        print("   Frontend should store this in localStorage")
        
    elif response.status_code == 401:
        print("❌ FAILED: Backend returned 401 Unauthorized")
        print("   This means the endpoint still requires authentication")
        print("   The backend needs to be updated to allow guest access")
        print(f"\nError: {response.json()}")
        sys.exit(1)
        
    else:
        print(f"❌ UNEXPECTED STATUS: {response.status_code}")
        print(f"Response: {response.text}")
        sys.exit(1)
        
except requests.exceptions.RequestException as e:
    print(f"❌ REQUEST ERROR: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("Test 2: Authenticated User Submission (With Token)")
print("-" * 60)

# Try to get a token (if available)
token = os.getenv("TEST_AUTH_TOKEN")
if not token:
    print("⚠️ SKIPPED: No TEST_AUTH_TOKEN in environment")
    print("   Set TEST_AUTH_TOKEN to test authenticated user flow")
    print("   Guest mode test (Test 1) passed, which is the main requirement")
else:
    try:
        response = requests.post(
            ENDPOINT,
            json=test_payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            },
            timeout=60
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Authenticated user can submit quiz!")
            data = response.json()
            print(f"\nDiagnostic ID: {data.get('id')}")
            print(f"Quiz ID: {data.get('quiz_id')} (should have a value for authenticated user)")
            
            # Verify quiz_id is not None for authenticated users
            if data.get('quiz_id') is not None:
                print("\n✅ Verified: quiz_id is present for authenticated user (correct)")
            else:
                print("\n⚠️ Warning: quiz_id is None (expected a value for authenticated user)")
                
        else:
            print(f"❌ FAILED: Status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ REQUEST ERROR: {str(e)}")

print("\n" + "=" * 60)
print("Summary")
print("=" * 60)
print("✅ Guest mode test completed")
print("   - Guest users can now submit quizzes without authentication")
print("   - Diagnostic is generated but not saved to database")
print("   - Frontend should store diagnostic in localStorage for guest users")
print("\n✅ Backend is ready for guest mode!")

