#!/usr/bin/env python3
"""
Comprehensive Integration Test for Supabase and Gemini API
Tests all backend functionality with live connections
"""
import os
import sys
import json
import requests
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BASE_URL = "http://localhost:5000"

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def print_success(text):
    print(f"[OK] {text}")

def print_error(text):
    print(f"[ERROR] {text}")

def print_warning(text):
    print(f"[WARN] {text}")

def test_environment_setup():
    """Test that environment variables are configured"""
    print_header("1. ENVIRONMENT SETUP CHECK")
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    gemini_key = os.getenv("GOOGLE_API_KEY")
    use_in_memory = os.getenv("USE_IN_MEMORY_DB", "true").lower() == "true"
    
    checks = []
    
    if supabase_url:
        checks.append(("SUPABASE_URL", True, supabase_url[:30] + "..."))
    else:
        checks.append(("SUPABASE_URL", False, "Not set"))
    
    if supabase_key:
        checks.append(("SUPABASE_ANON_KEY", True, f"{supabase_key[:20]}..."))
    else:
        checks.append(("SUPABASE_ANON_KEY", False, "Not set"))
    
    if gemini_key:
        checks.append(("GOOGLE_API_KEY", True, f"{gemini_key[:20]}..."))
    else:
        checks.append(("GOOGLE_API_KEY", False, "Not set"))
    
    checks.append(("USE_IN_MEMORY_DB", True, str(use_in_memory)))
    
    for name, status, value in checks:
        if status:
            print_success(f"{name}: {value}")
        else:
            print_error(f"{name}: {value}")
    
    return all(check[1] for check in checks if check[0] != "USE_IN_MEMORY_DB")

def test_supabase_connection():
    """Test direct Supabase connection"""
    print_header("2. SUPABASE CONNECTION TEST")
    
    try:
        from supabase import create_client
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        
        if not (supabase_url and supabase_key):
            print_warning("Supabase credentials not set. Skipping direct connection test.")
            return False
        
        client = create_client(supabase_url, supabase_key)
        
        # Test query
        response = client.table("users").select("id").limit(1).execute()
        print_success(f"Supabase connection successful! (Found {len(response.data)} users)")
        return True
        
    except Exception as e:
        print_error(f"Supabase connection failed: {e}")
        return False

def test_gemini_connection():
    """Test Gemini API connection"""
    print_header("3. GEMINI API CONNECTION TEST")
    
    try:
        from google import genai
        
        # Support both GOOGLE_API_KEY and GEMINI_API_KEY for compatibility
        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            print_warning("Gemini API key not set (check GOOGLE_API_KEY or GEMINI_API_KEY). Skipping connection test.")
            return False
        
        # New API: genai.Client() automatically picks up GEMINI_API_KEY from env
        client = genai.Client(api_key=api_key)
        
        # Simple test prompt using new API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'Hello' if you can read this."
        )
        print_success(f"Gemini API connection successful!")
        print(f"   Response: {response.text[:100] if hasattr(response, 'text') else str(response)[:100]}...")
        return True
        
    except Exception as e:
        print_error(f"Gemini API connection failed: {e}")
        import traceback
        print_error(f"Full error: {traceback.format_exc()}")
        return False

def test_flask_server():
    """Test Flask server is running"""
    print_header("4. FLASK SERVER TEST")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Flask server is running! Version: {data.get('version', 'unknown')}")
            return True
        else:
            print_error(f"Flask server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Flask server is not running. Start it with: flask run")
        return False
    except Exception as e:
        print_error(f"Error connecting to Flask server: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print_header("5. API ENDPOINTS TEST")
    
    # Test user registration
    print("\n[TEST] Testing User Registration...")
    try:
        reg_data = {
            "email": f"test_{os.urandom(4).hex()}@example.com",
            "name": "Test User",
            "phone": "1234567890"
        }
        response = requests.post(f"{BASE_URL}/api/users/register", json=reg_data)
        if response.status_code == 201:
            user = response.json()
            user_id = user.get("id")
            print_success(f"User registered: {user_id}")
        else:
            print_error(f"Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Registration error: {e}")
        return False
    
    # Test questions endpoint
    print("\n[TEST] Testing Questions Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/questions?total=5")
        if response.status_code == 200:
            questions = response.json()
            print_success(f"Retrieved {len(questions)} questions")
            # Save first question ID for later tests
            question_id = questions[0].get("id") if questions else None
            if not question_id:
                print_warning("No questions returned, cannot test quiz submit")
                return False
        else:
            print_error(f"Questions endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Questions error: {e}")
        return False
    
    # Test quiz start
    print("\n📝 Testing Quiz Start...")
    try:
        quiz_data = {"userId": user_id, "totalQuestions": 5}
        response = requests.post(f"{BASE_URL}/api/quiz/start", json=quiz_data)
        if response.status_code == 201:
            quiz = response.json()
            quiz_id = quiz.get("id")
            print_success(f"Quiz started: {quiz_id}")
        else:
            print_error(f"Quiz start failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Quiz start error: {e}")
        return False
    
    # Test quiz submit
    print("\n📝 Testing Quiz Submit...")
    try:
        # Use actual question ID from database, not hardcoded "q1"
        submit_data = {
            "responses": [
                {
                    "questionId": question_id,  # Use real UUID from database
                    "studentAnswer": "A",
                    "correctAnswer": "A",
                    "isCorrect": True,
                    "explanationText": "Test explanation",
                    "timeSpentSeconds": 30
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/api/quiz/{quiz_id}/submit", json=submit_data)
        if response.status_code == 200:
            print_success("Quiz submitted successfully")
        else:
            print_error(f"Quiz submit failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Quiz submit error: {e}")
        return False
    
    # Test AI analyze
    print("\n📝 Testing AI Analyze Endpoint...")
    try:
        analyze_data = {
            "userId": user_id,
            "quizId": quiz_id,
            "responses": [
                {
                    "questionId": question_id,  # Use real UUID
                    "studentAnswer": "A",
                    "correctAnswer": "B",
                    "isCorrect": False
                }
            ]
        }
        response = requests.post(f"{BASE_URL}/api/ai/analyze-diagnostic", json=analyze_data)
        if response.status_code == 200:
            analysis = response.json()
            print_success("AI analysis completed")
            print(f"   Weak topics: {len(analysis.get('weakTopics', []))}")
            diagnostic_id = analysis.get("id")  # Get diagnostic ID from response
            if not diagnostic_id:
                print_warning("Diagnostic ID not in response, skipping study plan test")
                diagnostic_id = None
        else:
            print_error(f"AI analyze failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"AI analyze error: {e}")
        return False
    
    # Test AI generate study plan (only if diagnostic ID was returned)
    if diagnostic_id:
        print("\n[TEST] Testing Study Plan Generation...")
        try:
            plan_data = {
                "userId": user_id,
                "diagnosticId": diagnostic_id,
                "weakTopics": [{"topicId": question_id, "topicName": "Algebra", "accuracy": 0.5}],  # Use real question ID
                "targetScore": 250,
                "weeksAvailable": 4
            }
            response = requests.post(f"{BASE_URL}/api/ai/generate-study-plan", json=plan_data)
            if response.status_code == 201:
                plan = response.json()
                print_success("Study plan generated")
                print(f"   Plan ID: {plan.get('id', 'N/A')}")
            else:
                print_error(f"Study plan generation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print_error(f"Study plan error: {e}")
            return False
    else:
        print_warning("Skipping study plan test (no diagnostic ID)")
    
    # Test progress endpoint
    print("\n📝 Testing Progress Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/users/{user_id}/progress")
        if response.status_code == 200:
            progress = response.json()
            print_success(f"Progress retrieved: {len(progress)} items")
        else:
            print_error(f"Progress endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Progress error: {e}")
        return False
    
    # Test analytics endpoint
    print("\n📝 Testing Analytics Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/analytics/dashboard")
        if response.status_code == 200:
            analytics = response.json()
            print_success("Analytics retrieved")
            print(f"   Total users: {analytics.get('total_users', 0)}")
        else:
            print_error(f"Analytics endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Analytics error: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("  STUDYGAPAI BACKEND INTEGRATION TEST SUITE")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Environment Setup", test_environment_setup()))
    results.append(("Supabase Connection", test_supabase_connection()))
    results.append(("Gemini API Connection", test_gemini_connection()))
    results.append(("Flask Server", test_flask_server()))
    results.append(("API Endpoints", test_api_endpoints()))
    
    # Print summary
    print_header("TEST SUMMARY")
    total = len(results)
    passed = sum(1 for _, result in results if result)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\n{'=' * 70}")
    print(f"  Total: {total} | Passed: {passed} | Failed: {total - passed}")
    print(f"{'=' * 70}\n")
    
    if passed == total:
        print_success("All tests passed! Backend is fully operational.")
        return 0
    else:
        print_error("Some tests failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

