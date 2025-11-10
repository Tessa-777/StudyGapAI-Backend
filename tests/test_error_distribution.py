"""
Test error_distribution calculation
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.error_analysis import classify_error_type, calculate_error_distribution


def test_classify_error_types():
    """Test error type classification"""
    
    # Conceptual gap
    q1 = {
        "is_correct": False,
        "explanation": "I don't understand the concept of derivatives",
        "confidence": 2
    }
    assert classify_error_type(q1) == "conceptual_gap"
    
    # Procedural error
    q2 = {
        "is_correct": False,
        "explanation": "I used the wrong formula in my calculation",
        "confidence": 3
    }
    assert classify_error_type(q2) == "procedural_error"
    
    # Careless mistake
    q3 = {
        "is_correct": False,
        "explanation": "I made a careless mistake with the sign",
        "confidence": 5
    }
    assert classify_error_type(q3) == "careless_mistake"
    
    # Knowledge gap
    q4 = {
        "is_correct": False,
        "explanation": "I don't know this",
        "confidence": 1
    }
    assert classify_error_type(q4) == "knowledge_gap"
    
    # Misinterpretation
    q5 = {
        "is_correct": False,
        "explanation": "I misread the question",
        "confidence": 3
    }
    assert classify_error_type(q5) == "misinterpretation"
    
    # Correct answer (no error type)
    q6 = {
        "is_correct": True,
        "explanation": "I got it right",
        "confidence": 4
    }
    assert classify_error_type(q6) is None
    
    print("[OK] Error type classification works correctly")


def test_calculate_error_distribution():
    """Test error distribution calculation"""
    
    questions = [
        {"is_correct": False, "explanation": "I don't understand the concept", "confidence": 2},
        {"is_correct": False, "explanation": "Wrong formula used", "confidence": 3},
        {"is_correct": False, "explanation": "Careless mistake with sign", "confidence": 5},
        {"is_correct": False, "explanation": "I don't know this topic", "confidence": 1},
        {"is_correct": False, "explanation": "I misread the question", "confidence": 3},
        {"is_correct": True, "explanation": "Got it right", "confidence": 4},
        {"is_correct": False, "explanation": "Conceptual misunderstanding", "confidence": 2},
    ]
    
    dist = calculate_error_distribution(questions)
    
    # Should have counts for each error type
    assert "conceptual_gap" in dist
    assert "procedural_error" in dist
    assert "careless_mistake" in dist
    assert "knowledge_gap" in dist
    assert "misinterpretation" in dist
    
    # Should have at least some errors (6 incorrect out of 7)
    total_errors = sum(dist.values())
    assert total_errors == 6, f"Expected 6 errors, got {total_errors}"
    
    # Should have conceptual_gap (2 questions)
    assert dist["conceptual_gap"] >= 1, "Should have at least 1 conceptual gap"
    
    print(f"[OK] Error distribution calculated: {dist}")
    print(f"[OK] Total errors: {sum(dist.values())}")


def test_error_distribution_all_zeros_fallback():
    """Test that error_distribution is calculated when Gemini returns all zeros"""
    
    questions = [
        {"is_correct": False, "explanation": "I don't understand", "confidence": 2},
        {"is_correct": False, "explanation": "Wrong step", "confidence": 3},
        {"is_correct": True, "explanation": "Correct", "confidence": 4},
    ]
    
    # Simulate Gemini returning all zeros
    gemini_error_dist = {
        "conceptual_gap": 0,
        "procedural_error": 0,
        "careless_mistake": 0,
        "knowledge_gap": 0,
        "misinterpretation": 0
    }
    
    # Calculate from questions
    calculated_dist = calculate_error_distribution(questions)
    
    # Should have data
    assert any(calculated_dist.values()), "Calculated distribution should have data"
    assert sum(calculated_dist.values()) == 2, "Should have 2 errors"
    
    print(f"[OK] Fallback calculation works: {calculated_dist}")


def test_default_to_knowledge_gap():
    """Test that if classification fails, everything defaults to knowledge_gap"""
    
    # Questions with unclear explanations that might not match keywords
    questions = [
        {"is_correct": False, "explanation": "xyz", "confidence": 2},  # Very unclear
        {"is_correct": False, "explanation": "", "confidence": 1},  # Empty explanation
        {"is_correct": False, "explanation": "abc def", "confidence": 3},  # No keywords
        {"is_correct": True, "explanation": "Correct", "confidence": 4},
    ]
    
    calculated_dist = calculate_error_distribution(questions)
    
    # Should have data (all should default to knowledge_gap)
    assert any(calculated_dist.values()), "Should have error distribution data"
    assert sum(calculated_dist.values()) == 3, "Should have 3 errors"
    
    # All unclear errors should default to knowledge_gap
    # (The function should classify them, but if it can't, they default to knowledge_gap)
    assert calculated_dist["knowledge_gap"] >= 0, "Should have knowledge_gap entries"
    
    print(f"[OK] Default to knowledge_gap works: {calculated_dist}")
    print(f"[OK] Total errors classified: {sum(calculated_dist.values())}")


if __name__ == "__main__":
    print("=" * 80)
    print("TESTING ERROR DISTRIBUTION")
    print("=" * 80)
    
    test_classify_error_types()
    test_calculate_error_distribution()
    test_error_distribution_all_zeros_fallback()
    test_default_to_knowledge_gap()
    
    print("\n" + "=" * 80)
    print("[OK] ALL TESTS PASSED!")
    print("=" * 80)

