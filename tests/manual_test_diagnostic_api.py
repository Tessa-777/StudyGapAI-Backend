#!/usr/bin/env python3
"""
Complete automated test for diagnostic API
Creates user, quiz, submits, gets diagnostic, and tests results endpoint
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
API_BASE_URL = "http://localhost:5000"

def create_test_user():
    """Create a test user and get token"""
    print("🔧 Step 1: Creating test user...")
    
    import time
    test_email = f"test_{int(time.time())}@example.com"
    test_password = "TestPassword123!"
    
    # Create user via admin API
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
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create user: {response.status_code}")
        print(f"Error: {response.text}")
        sys.exit(1)
    
    user_id = response.json().get("id")
    print(f"✅ User created: {user_id}")
    
    # Sign in to get token
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    auth_response = supabase.auth.sign_in_with_password({
        "email": test_email,
        "password": test_password
    })
    
    if not auth_response.session:
        print("❌ Failed to get session token")
        sys.exit(1)
    
    token = auth_response.session.access_token
    print(f"✅ Token obtained")
    
    return token, user_id, test_email

def register_user(token, user_id, email):
    """Register user in users table"""
    print("\n🔧 Step 2: Registering user in users table...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/users/register",
        headers=headers,
        json={
            "email": email,
            "name": "Test User",
            "userId": user_id
        }
    )
    
    if response.status_code not in [200, 201]:
        # User might already exist, that's okay
        if "already exists" in response.text.lower() or "duplicate" in response.text.lower():
            print("✅ User already exists in users table")
        else:
            print(f"⚠️ Failed to register user: {response.status_code}")
            print(f"Error: {response.text}")
            # Continue anyway - might work
    else:
        print("✅ User registered in users table")

def create_quiz(token):
    """Create a diagnostic quiz"""
    print("\n🔧 Step 3: Creating quiz...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Try the quiz start endpoint
    response = requests.post(
        f"{API_BASE_URL}/api/quiz/start",
        headers=headers,
        json={"subject": "Mathematics", "totalQuestions": 5}
    )
    
    if response.status_code not in [200, 201]:
        print(f"❌ Failed to create quiz: {response.status_code}")
        print(f"Error: {response.text}")
        # Try to get more info
        try:
            error_data = response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            pass
        sys.exit(1)
    
    quiz_data = response.json()
    quiz_id = quiz_data.get("quiz_id") or quiz_data.get("id")
    if not quiz_id:
        print(f"❌ Quiz created but no ID returned: {quiz_data}")
        sys.exit(1)
    
    print(f"✅ Quiz created: {quiz_id}")
    
    return quiz_id

def submit_quiz(token, quiz_id):
    """Submit quiz responses and get diagnostic"""
    print("\n🔧 Step 4: Submitting quiz...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Sample quiz responses - must match QuestionResponse schema
    questions_list = [
        {
            "id": 1,
            "topic": "Algebra",
            "student_answer": "A",
            "correct_answer": "B",
            "is_correct": False,
            "confidence": 2,
            "explanation": "I guessed",
            "time_spent_seconds": 30
        },
        {
            "id": 2,
            "topic": "Geometry",
            "student_answer": "C",
            "correct_answer": "C",
            "is_correct": True,
            "confidence": 4,
            "explanation": "I knew this one",
            "time_spent_seconds": 45
        },
        {
            "id": 3,
            "topic": "Algebra",
            "student_answer": "D",
            "correct_answer": "A",
            "is_correct": False,
            "confidence": 1,
            "explanation": "Not sure",
            "time_spent_seconds": 60
        },
        {
            "id": 4,
            "topic": "Calculus",
            "student_answer": "B",
            "correct_answer": "B",
            "is_correct": True,
            "confidence": 5,
            "explanation": "Easy question",
            "time_spent_seconds": 20
        },
        {
            "id": 5,
            "topic": "Geometry",
            "student_answer": "A",
            "correct_answer": "C",
            "is_correct": False,
            "confidence": 2,
            "explanation": "Confused",
            "time_spent_seconds": 50
        }
    ]
    
    # Payload must match AnalyzeDiagnosticRequest schema
    payload = {
        "subject": "Mathematics",
        "total_questions": 5,
        "time_taken": 3.42,  # 205 seconds = ~3.42 minutes
        "questions_list": questions_list,
        "quiz_id": quiz_id
    }
    
    response = requests.post(
        f"{API_BASE_URL}/api/ai/analyze-diagnostic",
        headers=headers,
        json=payload
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to submit quiz: {response.status_code}")
        print(f"Error: {response.text}")
        sys.exit(1)
    
    diagnostic_data = response.json()
    diagnostic_id = diagnostic_data.get("id")
    print(f"✅ Quiz submitted, diagnostic created: {diagnostic_id}")
    
    return diagnostic_data, quiz_id

def test_results_endpoint(token, quiz_id):
    """Test the results endpoint"""
    print(f"\n🔧 Step 5: Testing results endpoint for quiz: {quiz_id}...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    response = requests.get(
        f"{API_BASE_URL}/api/quiz/{quiz_id}/results",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"❌ Failed to get results: {response.status_code}")
        print(f"Error: {response.text}")
        return False
    
    results = response.json()
    print("✅ Results endpoint works!")
    
    # Check diagnostic fields
    diagnostic = results.get("diagnostic")
    if not diagnostic:
        print("❌ No diagnostic data in response")
        return False
    
    print("\n📊 Diagnostic Fields Check:")
    fields_to_check = [
        "overall_performance",
        "topic_breakdown",
        "root_cause_analysis",
        "predicted_jamb_score",
        "study_plan",
        "recommendations"
    ]
    
    all_present = True
    for field in fields_to_check:
        if field in diagnostic and diagnostic[field] is not None:
            print(f"  ✅ {field}: Present")
        else:
            print(f"  ❌ {field}: Missing or None")
            all_present = False
    
    if all_present:
        print("\n🎉 All diagnostic fields are present!")
        print("\n📄 Diagnostic Summary:")
        print(f"  - Quiz ID: {diagnostic.get('quiz_id')}")
        print(f"  - Diagnostic ID: {diagnostic.get('id')}")
        if diagnostic.get("overall_performance"):
            perf = diagnostic["overall_performance"]
            print(f"  - Accuracy: {perf.get('accuracy', 'N/A')}%")
        if diagnostic.get("topic_breakdown"):
            print(f"  - Topics analyzed: {len(diagnostic['topic_breakdown'])}")
        return True
    else:
        print("\n⚠️ Some fields are missing")
        return False

def main():
    print("=" * 60)
    print("🚀 Automated Diagnostic API Test")
    print("=" * 60)
    
    # Check if backend is running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        print("✅ Backend is running")
    except requests.exceptions.RequestException:
        print("❌ Backend is not running! Please start Flask:")
        print("   flask run")
        sys.exit(1)
    
    try:
        # Step 1: Create user and get token
        token, user_id, email = create_test_user()
        
        # Step 2: Register user in users table
        register_user(token, user_id, email)
        
        # Step 3: Create quiz
        quiz_id = create_quiz(token)
        
        # Step 4: Submit quiz and get diagnostic
        diagnostic_data, quiz_id = submit_quiz(token, quiz_id)
        
        # Step 5: Test results endpoint
        success = test_results_endpoint(token, quiz_id)
        
        print("\n" + "=" * 60)
        if success:
            print("✅ ALL TESTS PASSED!")
            print(f"\n📝 Test Summary:")
            print(f"  - User ID: {user_id}")
            print(f"  - Email: {email}")
            print(f"  - Quiz ID: {quiz_id}")
            print(f"  - Diagnostic ID: {diagnostic_data.get('id')}")
            print(f"\n🔑 Token (save for testing):")
            print(f"   {token}")
        else:
            print("❌ SOME TESTS FAILED")
            sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

