"""
Comprehensive API Endpoint Testing Script

Tests all backend endpoints with proper JWT authentication.
Run get_jwt_token.py first to obtain a JWT token.
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:5000")
JWT_TOKEN = None

# Try to get token from file or environment
if os.path.exists(".test_token"):
    with open(".test_token", "r") as f:
        JWT_TOKEN = f.read().strip()

if not JWT_TOKEN:
    JWT_TOKEN = os.getenv("JWT_TOKEN")

if not JWT_TOKEN:
    print("ERROR: JWT_TOKEN not found!")
    print("Run get_jwt_token.py first to obtain a token.")
    sys.exit(1)

# Headers for authenticated requests
AUTH_HEADERS = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "Content-Type": "application/json"
}

# Headers for public requests
PUBLIC_HEADERS = {
    "Content-Type": "application/json"
}


def print_test(name: str):
    """Print test header"""
    print("\n" + "="*60)
    print(f"TEST: {name}")
    print("="*60)


def print_result(success: bool, response, expected_status: int = None):
    """Print test result"""
    status = response.status_code
    if expected_status:
        success = status == expected_status
    
    status_icon = "✅" if success else "❌"
    print(f"{status_icon} Status: {status} (expected: {expected_status or '200/201'})")
    
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)[:500]}")
    except:
        print(f"Response: {response.text[:500]}")
    
    return success


def test_health():
    """Test health endpoint"""
    print_test("Health Check (Public)")
    response = requests.get(f"{BASE_URL}/health", headers=PUBLIC_HEADERS)
    return print_result(True, response, 200)


def test_get_questions():
    """Test get questions endpoint"""
    print_test("Get Questions (Public)")
    response = requests.get(f"{BASE_URL}/api/questions?total=5", headers=PUBLIC_HEADERS)
    return print_result(True, response, 200)


def test_get_current_user():
    """Test get current user endpoint"""
    print_test("Get Current User (Authenticated)")
    response = requests.get(f"{BASE_URL}/api/users/me", headers=AUTH_HEADERS)
    success = print_result(True, response, 200)
    
    if success:
        data = response.json()
        return data.get("id")  # Return user ID for other tests
    return None


def test_update_target_score(user_id: str):
    """Test update target score"""
    print_test("Update Target Score (Authenticated)")
    data = {"targetScore": 250}
    response = requests.put(
        f"{BASE_URL}/api/users/target-score",
        json=data,
        headers=AUTH_HEADERS
    )
    return print_result(True, response, 200)


def test_start_quiz():
    """Test start quiz"""
    print_test("Start Quiz (Authenticated)")
    data = {"totalQuestions": 5}  # Use 5 for faster testing
    response = requests.post(
        f"{BASE_URL}/api/quiz/start",
        json=data,
        headers=AUTH_HEADERS
    )
    success = print_result(True, response, 201)
    
    if success:
        data = response.json()
        return data.get("id")  # Return quiz ID
    return None


def test_submit_quiz(quiz_id: str, question_ids: list):
    """Test submit quiz"""
    print_test("Submit Quiz (Authenticated)")
    
    # Create sample responses
    responses = []
    for i, q_id in enumerate(question_ids[:5]):  # Use first 5 questions
        responses.append({
            "questionId": q_id,
            "studentAnswer": "A" if i % 2 == 0 else "B",
            "correctAnswer": "C",
            "isCorrect": False,
            "explanationText": f"Test explanation for question {i+1}",
            "timeSpentSeconds": 30
        })
    
    data = {"responses": responses}
    response = requests.post(
        f"{BASE_URL}/api/quiz/{quiz_id}/submit",
        json=data,
        headers=AUTH_HEADERS
    )
    return print_result(True, response, 200)


def test_get_quiz_results(quiz_id: str):
    """Test get quiz results"""
    print_test("Get Quiz Results (Authenticated)")
    response = requests.get(
        f"{BASE_URL}/api/quiz/{quiz_id}/results",
        headers=AUTH_HEADERS
    )
    return print_result(True, response, 200)


def test_analyze_diagnostic(quiz_id: str, question_ids: list):
    """Test analyze diagnostic"""
    print_test("Analyze Diagnostic (Authenticated)")
    
    # Create sample responses for analysis
    responses = []
    for i, q_id in enumerate(question_ids[:5]):
        responses.append({
            "questionId": q_id,
            "studentAnswer": "A",
            "correctAnswer": "C",
            "isCorrect": False,
            "explanationText": f"I thought the answer was A because..."
        })
    
    data = {
        "quizId": quiz_id,
        "responses": responses
    }
    response = requests.post(
        f"{BASE_URL}/api/ai/analyze-diagnostic",
        json=data,
        headers=AUTH_HEADERS
    )
    success = print_result(True, response, 200)
    
    if success:
        data = response.json()
        return data.get("id")  # Return diagnostic ID
    return None


def test_generate_study_plan(diagnostic_id: str, user_id: str):
    """Test generate study plan"""
    print_test("Generate Study Plan (Authenticated)")
    
    data = {
        "diagnosticId": diagnostic_id,
        "weakTopics": [
            {"topicId": "topic-1", "topicName": "Algebra", "severity": "high"},
            {"topicId": "topic-2", "topicName": "Geometry", "severity": "medium"}
        ],
        "targetScore": 250,
        "currentScore": 150,
        "weeksAvailable": 6
    }
    response = requests.post(
        f"{BASE_URL}/api/ai/generate-study-plan",
        json=data,
        headers=AUTH_HEADERS
    )
    success = print_result(True, response, 201)
    
    if success:
        data = response.json()
        return data.get("id")  # Return study plan ID
    return None


def test_explain_answer():
    """Test explain answer (public)"""
    print_test("Explain Answer (Public)")
    
    data = {
        "questionId": "test-q-1",
        "studentAnswer": "A",
        "correctAnswer": "B",
        "studentReasoning": "I thought A was correct because..."
    }
    response = requests.post(
        f"{BASE_URL}/api/ai/explain-answer",
        json=data,
        headers=PUBLIC_HEADERS
    )
    return print_result(True, response, 200)


def test_get_progress(user_id: str):
    """Test get progress"""
    print_test("Get Progress (Authenticated)")
    response = requests.get(
        f"{BASE_URL}/api/progress",
        headers=AUTH_HEADERS
    )
    return print_result(True, response, 200)


def test_mark_progress_complete():
    """Test mark progress complete"""
    print_test("Mark Progress Complete (Authenticated)")
    
    data = {
        "topicId": "topic-1",
        "status": "completed",
        "resourcesViewed": 3,
        "practiceProblemsCompleted": 10
    }
    response = requests.post(
        f"{BASE_URL}/api/progress/mark-complete",
        json=data,
        headers=AUTH_HEADERS
    )
    return print_result(True, response, 201)


def test_adjust_plan(study_plan_id: str):
    """Test adjust plan"""
    print_test("Adjust Study Plan (Authenticated)")
    
    data = {
        "studyPlanId": study_plan_id,
        "completedTopics": ["topic-1"],
        "newWeakTopics": ["topic-3"]
    }
    response = requests.post(
        f"{BASE_URL}/api/ai/adjust-plan",
        json=data,
        headers=AUTH_HEADERS
    )
    return print_result(True, response, 200)


def test_analytics_dashboard():
    """Test analytics dashboard (public)"""
    print_test("Analytics Dashboard (Public)")
    response = requests.get(f"{BASE_URL}/api/analytics/dashboard", headers=PUBLIC_HEADERS)
    return print_result(True, response, 200)


def test_unauthorized_access():
    """Test that endpoints reject requests without auth"""
    print_test("Unauthorized Access Test (Should Fail)")
    
    # Try to access protected endpoint without token
    response = requests.get(f"{BASE_URL}/api/users/me")
    success = response.status_code == 401
    print_result(success, response, 401)
    return success


def main():
    """Run all tests"""
    print("="*60)
    print("StudyGapAI Backend API Testing Suite")
    print("="*60)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Token: {JWT_TOKEN[:30]}...")
    print("\nStarting tests...\n")
    
    results = []
    
    # Public endpoints
    results.append(("Health Check", test_health()))
    results.append(("Get Questions", test_get_questions()))
    results.append(("Explain Answer", test_explain_answer()))
    results.append(("Analytics Dashboard", test_analytics_dashboard()))
    
    # Authenticated endpoints
    user_id = test_get_current_user()
    results.append(("Get Current User", user_id is not None))
    
    if not user_id:
        print("\n❌ Cannot continue without user ID. Check authentication.")
        return
    
    results.append(("Update Target Score", test_update_target_score(user_id)))
    
    # Get questions for quiz
    questions_response = requests.get(f"{BASE_URL}/api/questions?total=5", headers=PUBLIC_HEADERS)
    question_ids = []
    if questions_response.status_code == 200:
        questions = questions_response.json()
        question_ids = [q.get("id") for q in questions if q.get("id")]
    
    quiz_id = test_start_quiz()
    results.append(("Start Quiz", quiz_id is not None))
    
    if quiz_id and question_ids:
        results.append(("Submit Quiz", test_submit_quiz(quiz_id, question_ids)))
        results.append(("Get Quiz Results", test_get_quiz_results(quiz_id)))
        
        diagnostic_id = test_analyze_diagnostic(quiz_id, question_ids)
        results.append(("Analyze Diagnostic", diagnostic_id is not None))
        
        if diagnostic_id:
            study_plan_id = test_generate_study_plan(diagnostic_id, user_id)
            results.append(("Generate Study Plan", study_plan_id is not None))
            
            if study_plan_id:
                results.append(("Adjust Plan", test_adjust_plan(study_plan_id)))
    
    results.append(("Get Progress", test_get_progress(user_id)))
    results.append(("Mark Progress Complete", test_mark_progress_complete()))
    
    # Security test
    results.append(("Unauthorized Access", test_unauthorized_access()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "-"*60)
    print(f"Total: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()

