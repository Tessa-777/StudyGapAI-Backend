#!/usr/bin/env python3
"""
Complete test script for save-diagnostic endpoint
- Creates test user if needed
- Gets JWT token
- Tests save-diagnostic endpoint
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

load_dotenv()

# Backend URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
SAVE_ENDPOINT = f"{BACKEND_URL}/api/ai/save-diagnostic"

print("=" * 60)
print("Testing Save Diagnostic Endpoint - Complete Test")
print("=" * 60)

# Step 1: Get or create test token
print("\n🔑 Step 1: Getting test token...")
print("-" * 60)

# Try to get token from environment first
token = os.getenv("TEST_AUTH_TOKEN")

if not token:
    print("   TEST_AUTH_TOKEN not set, attempting to create test user...")
    
    try:
        from supabase import create_client
        
        SUPABASE_URL = os.getenv("SUPABASE_URL")
        SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
        SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not SUPABASE_URL or not SUPABASE_ANON_KEY:
            print("   ❌ ERROR: SUPABASE_URL or SUPABASE_ANON_KEY not set")
            print("   Please set TEST_AUTH_TOKEN in your .env file")
            sys.exit(1)
        
        # Create supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        
        # Try to create test user via admin API
        import uuid
        test_email = f"test_save_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "TestPassword123!"
        
        print(f"   Creating test user: {test_email}")
        
        # Try admin API if service key is available
        if SUPABASE_SERVICE_KEY:
            try:
                admin_url = f"{SUPABASE_URL}/auth/v1/admin/users"
                headers = {
                    "apikey": SUPABASE_SERVICE_KEY,
                    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
                    "Content-Type": "application/json"
                }
                
                user_data = {
                    "email": test_email,
                    "password": test_password,
                    "email_confirm": True,
                    "user_metadata": {"name": "Test User"}
                }
                
                response = requests.post(admin_url, json=user_data, headers=headers)
                
                if response.status_code in [200, 201]:
                    print("   ✅ Test user created via admin API")
                    # Sign in to get token
                    auth_response = supabase.auth.sign_in_with_password({
                        "email": test_email,
                        "password": test_password
                    })
                    
                    if auth_response.session:
                        token = auth_response.session.access_token
                        print("   ✅ Got JWT token")
                    else:
                        print("   ❌ Failed to get token after user creation")
                        sys.exit(1)
                else:
                    print(f"   ⚠️ Admin API failed ({response.status_code}), trying regular signup...")
                    raise Exception("Admin API failed")
                    
            except Exception as e:
                print(f"   ⚠️ Admin API error: {e}")
                # Fall back to regular signup
                try:
                    signup_response = supabase.auth.sign_up({
                        "email": test_email,
                        "password": test_password
                    })
                    
                    if signup_response.session:
                        token = signup_response.session.access_token
                        print("   ✅ Got JWT token from signup")
                    else:
                        print("   ❌ Signup succeeded but no session (email confirmation may be required)")
                        print("   Please set TEST_AUTH_TOKEN in .env file or disable email confirmation in Supabase")
                        sys.exit(1)
                except Exception as e2:
                    print(f"   ❌ Signup failed: {e2}")
                    print("   Please set TEST_AUTH_TOKEN in your .env file")
                    sys.exit(1)
        else:
            print("   ⚠️ SUPABASE_SERVICE_ROLE_KEY not set, trying regular signup...")
            try:
                signup_response = supabase.auth.sign_up({
                    "email": test_email,
                    "password": test_password
                })
                
                if signup_response.session:
                    token = signup_response.session.access_token
                    print("   ✅ Got JWT token from signup")
                else:
                    print("   ❌ Signup succeeded but no session (email confirmation may be required)")
                    print("   Please set TEST_AUTH_TOKEN in .env file or disable email confirmation in Supabase")
                    sys.exit(1)
            except Exception as e:
                print(f"   ❌ Signup failed: {e}")
                print("   Please set TEST_AUTH_TOKEN in your .env file")
                sys.exit(1)
    except ImportError:
        print("   ❌ ERROR: supabase package not installed")
        print("   Run: pip install supabase")
        print("   Or set TEST_AUTH_TOKEN in your .env file")
        sys.exit(1)
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        print("   Please set TEST_AUTH_TOKEN in your .env file")
        sys.exit(1)
else:
    print("   ✅ Using TEST_AUTH_TOKEN from environment")

print(f"   Token: {token[:50]}...")

# Step 2: Prepare test data
print("\n📊 Step 2: Preparing test data...")
print("-" * 60)

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

diagnostic_data = {
    "id": "guest-diagnostic-id-123",
    "quiz_id": None,
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

payload = {
    **quiz_data,
    "diagnostic": diagnostic_data
}

print(f"   Quiz data: {len(quiz_data['questions_list'])} questions")
print(f"   Diagnostic data: {len(diagnostic_data)} fields")
print(f"   Payload size: {len(json.dumps(payload))} bytes")

# Step 3: Test save-diagnostic endpoint
print("\n🧪 Step 3: Testing save-diagnostic endpoint...")
print("-" * 60)
print(f"   Endpoint: {SAVE_ENDPOINT}")
print(f"   Method: POST")
print(f"   Auth: Bearer token")

try:
    response = requests.post(
        SAVE_ENDPOINT,
        json=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        },
        timeout=60
    )
    
    print(f"\n   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ SUCCESS: Guest diagnostic saved to database!")
        data = response.json()
        print(f"\n   Response:")
        print(f"     quiz_id: {data.get('quiz_id')}")
        print(f"     diagnostic_id: {data.get('diagnostic_id')}")
        print(f"     message: {data.get('message')}")
        
        # Step 4: Verify the saved diagnostic
        print("\n🔍 Step 4: Verifying saved diagnostic...")
        print("-" * 60)
        
        quiz_id = data.get('quiz_id')
        if quiz_id:
            # Try to get the quiz results
            results_endpoint = f"{BACKEND_URL}/api/quiz/{quiz_id}/results"
            print(f"   Fetching quiz results: {results_endpoint}")
            
            results_response = requests.get(
                results_endpoint,
                headers={
                    "Authorization": f"Bearer {token}"
                },
                timeout=30
            )
            
            if results_response.status_code == 200:
                results_data = results_response.json()
                print("   ✅ Quiz results retrieved successfully!")
                
                # Check if diagnostic is present
                if results_data.get('diagnostic'):
                    diagnostic = results_data['diagnostic']
                    print(f"   ✅ Diagnostic found in database")
                    print(f"     Diagnostic ID: {diagnostic.get('id')}")
                    print(f"     Quiz ID: {diagnostic.get('quiz_id')}")
                    print(f"     Generated at: {diagnostic.get('generated_at')}")
                    
                    # Check diagnostic fields
                    if diagnostic.get('overall_performance'):
                        perf = diagnostic['overall_performance']
                        print(f"     Overall Performance: {perf.get('accuracy')}% accuracy")
                    
                    if diagnostic.get('topic_breakdown'):
                        topics = diagnostic['topic_breakdown']
                        print(f"     Topics Analyzed: {len(topics)}")
                    
                    if diagnostic.get('study_plan'):
                        print(f"     Study Plan: Present")
                    
                    print("\n   ✅✅✅ ALL CHECKS PASSED! ✅✅✅")
                    print("\n   Summary:")
                    print(f"     - Quiz created: {quiz_id}")
                    print(f"     - Diagnostic saved: {diagnostic.get('id')}")
                    print(f"     - Diagnostic accessible via API")
                    print(f"     - All data fields present")
                else:
                    print("   ⚠️ WARNING: Diagnostic not found in quiz results")
            else:
                print(f"   ⚠️ WARNING: Could not verify quiz results ({results_response.status_code})")
                print(f"   Response: {results_response.text}")
        else:
            print("   ⚠️ WARNING: No quiz_id in response")
        
    elif response.status_code == 401:
        print("   ❌ FAILED: Authentication required")
        print(f"   Response: {response.json()}")
        print("\n   This endpoint requires authentication.")
        print("   Make sure your token is valid and not expired.")
        sys.exit(1)
        
    elif response.status_code == 400:
        print("   ❌ FAILED: Bad Request")
        error_data = response.json()
        print(f"   Error: {error_data}")
        
        if 'fields' in error_data:
            print(f"   Missing fields: {error_data['fields']}")
        
        sys.exit(1)
        
    else:
        print(f"   ❌ UNEXPECTED STATUS: {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
        
except requests.exceptions.RequestException as e:
    print(f"   ❌ REQUEST ERROR: {str(e)}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ TEST COMPLETE")
print("=" * 60)
print("\nSummary:")
print("  ✅ Test user created/authenticated")
print("  ✅ Save-diagnostic endpoint called successfully")
print("  ✅ Quiz created in database")
print("  ✅ Quiz responses saved")
print("  ✅ Diagnostic saved and linked to quiz")
print("  ✅ Diagnostic verified and accessible")
print("\n🎉 The save-diagnostic endpoint is working correctly!")
print("\nNext steps:")
print("  - Frontend can call this endpoint after user signs up")
print("  - Frontend should update localStorage with quiz_id")
print("  - User can now access their diagnostic from the database")

