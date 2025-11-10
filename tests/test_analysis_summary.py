"""
Test to verify analysis_summary is included in diagnostic response.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.ai_enhanced import EnhancedAIService

def test_mock_analysis_includes_summary():
    """Test that mock analysis includes analysis_summary"""
    service = EnhancedAIService(api_key=None, model_name="gemini-1.5-flash", mock=True)
    
    quiz_data = {
        "subject": "Mathematics",
        "total_questions": 10,
        "time_taken": 20.0,
        "questions_list": [
            {
                "topic": "Algebra",
                "student_answer": "A",
                "correct_answer": "B",
                "is_correct": False,
                "confidence": 2,
                "explanation": "I thought it was A",
                "time_spent_seconds": 120
            },
            {
                "topic": "Geometry",
                "student_answer": "C",
                "correct_answer": "C",
                "is_correct": True,
                "confidence": 4,
                "explanation": "I knew this one",
                "time_spent_seconds": 60
            }
        ]
    }
    
    result = service.analyze_diagnostic(quiz_data)
    
    # Verify analysis_summary is present
    assert "analysis_summary" in result, "analysis_summary should be in response"
    assert isinstance(result["analysis_summary"], str), "analysis_summary should be a string"
    assert len(result["analysis_summary"]) > 0, "analysis_summary should not be empty"
    
    print(f"[OK] analysis_summary is present: {result['analysis_summary'][:100]}...")
    print(f"[OK] analysis_summary length: {len(result['analysis_summary'])} characters")
    
    # Verify it contains expected information
    assert "accuracy" in result["analysis_summary"].lower() or "%" in result["analysis_summary"], \
        "analysis_summary should mention accuracy"
    
    print("[OK] All tests passed! analysis_summary is correctly included in response.")

if __name__ == "__main__":
    test_mock_analysis_includes_summary()

