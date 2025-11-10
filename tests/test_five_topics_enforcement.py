"""
Test that exactly 5 topics are always returned in topic_breakdown
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.topic_mapping import enforce_five_topics, map_topic_to_main, MAIN_TOPICS


def test_enforce_five_topics():
    """Test that enforce_five_topics always returns exactly 5 topics"""
    
    # Simulate AI returning more than 5 topics (prerequisite topics)
    ai_breakdown = [
        {"topic": "Number bases", "accuracy": 50.0, "fluency_index": 30.0, "status": "weak", "questions_attempted": 3},
        {"topic": "Fractions", "accuracy": 60.0, "fluency_index": 40.0, "status": "weak", "questions_attempted": 2},
        {"topic": "Polynomials", "accuracy": 70.0, "fluency_index": 50.0, "status": "developing", "questions_attempted": 4},
        {"topic": "Equations", "accuracy": 80.0, "fluency_index": 60.0, "status": "developing", "questions_attempted": 3},
        {"topic": "Geometry", "accuracy": 90.0, "fluency_index": 80.0, "status": "strong", "questions_attempted": 5},
        {"topic": "Trigonometry", "accuracy": 85.0, "fluency_index": 70.0, "status": "strong", "questions_attempted": 4},
        {"topic": "Calculus", "accuracy": 75.0, "fluency_index": 65.0, "status": "developing", "questions_attempted": 3},
        {"topic": "Statistics", "accuracy": 65.0, "fluency_index": 55.0, "status": "developing", "questions_attempted": 2},
    ]
    
    # Questions that map to these topics
    questions = [
        {"topic": "Number bases", "is_correct": False, "confidence": 2},
        {"topic": "Number bases", "is_correct": True, "confidence": 3},
        {"topic": "Number bases", "is_correct": False, "confidence": 2},
        {"topic": "Fractions", "is_correct": True, "confidence": 3},
        {"topic": "Fractions", "is_correct": True, "confidence": 4},
        {"topic": "Polynomials", "is_correct": True, "confidence": 4},
        {"topic": "Polynomials", "is_correct": False, "confidence": 3},
        {"topic": "Polynomials", "is_correct": True, "confidence": 4},
        {"topic": "Polynomials", "is_correct": True, "confidence": 5},
        {"topic": "Equations", "is_correct": True, "confidence": 4},
        {"topic": "Equations", "is_correct": True, "confidence": 5},
        {"topic": "Equations", "is_correct": False, "confidence": 3},
        {"topic": "Geometry", "is_correct": True, "confidence": 5},
        {"topic": "Geometry", "is_correct": True, "confidence": 4},
        {"topic": "Geometry", "is_correct": True, "confidence": 5},
        {"topic": "Geometry", "is_correct": False, "confidence": 4},
        {"topic": "Geometry", "is_correct": True, "confidence": 5},
        {"topic": "Trigonometry", "is_correct": True, "confidence": 4},
        {"topic": "Trigonometry", "is_correct": True, "confidence": 5},
        {"topic": "Trigonometry", "is_correct": False, "confidence": 3},
        {"topic": "Trigonometry", "is_correct": True, "confidence": 4},
        {"topic": "Calculus", "is_correct": True, "confidence": 4},
        {"topic": "Calculus", "is_correct": False, "confidence": 3},
        {"topic": "Calculus", "is_correct": True, "confidence": 4},
        {"topic": "Statistics", "is_correct": True, "confidence": 3},
        {"topic": "Statistics", "is_correct": False, "confidence": 2},
    ]
    
    result = enforce_five_topics(ai_breakdown, questions)
    
    # Must have exactly 5 topics
    assert len(result) == 5, f"Expected exactly 5 topics, got {len(result)}"
    
    # All topics must be from MAIN_TOPICS
    result_topics = {t["topic"] for t in result}
    assert result_topics == set(MAIN_TOPICS), f"Topics don't match main topics. Got: {result_topics}"
    
    print(f"[OK] Exactly 5 topics returned: {[t['topic'] for t in result]}")
    print(f"[OK] All topics are main topics: {result_topics == set(MAIN_TOPICS)}")


def test_map_topic_to_main():
    """Test topic mapping to main topics"""
    
    test_cases = [
        ("Number bases", "Number and Numeration"),
        ("Fractions", "Number and Numeration"),
        ("Polynomials", "Algebra"),
        ("Equations", "Algebra"),
        ("Geometry", "Geometry and Trigonometry"),
        ("Trigonometry", "Geometry and Trigonometry"),
        ("Calculus", "Calculus"),
        ("Statistics", "Statistics and Probability"),
        ("Probability", "Statistics and Probability"),
        ("Number and Numeration", "Number and Numeration"),  # Already main
        ("Algebra", "Algebra"),  # Already main
    ]
    
    for topic, expected_main in test_cases:
        result = map_topic_to_main(topic)
        assert result == expected_main, f"Expected {expected_main} for '{topic}', got {result}"
    
    print("[OK] All topic mappings work correctly")


def test_enforce_five_topics_with_fewer_topics():
    """Test that even if AI returns fewer than 5, we get exactly 5"""
    
    # AI returns only 2 topics
    ai_breakdown = [
        {"topic": "Algebra", "accuracy": 70.0, "fluency_index": 50.0, "status": "developing", "questions_attempted": 5},
        {"topic": "Geometry", "accuracy": 80.0, "fluency_index": 60.0, "status": "developing", "questions_attempted": 3},
    ]
    
    questions = [
        {"topic": "Polynomials", "is_correct": True, "confidence": 4},
        {"topic": "Equations", "is_correct": False, "confidence": 3},
        {"topic": "Geometry", "is_correct": True, "confidence": 4},
    ]
    
    result = enforce_five_topics(ai_breakdown, questions)
    
    # Must have exactly 5 topics
    assert len(result) == 5, f"Expected exactly 5 topics, got {len(result)}"
    
    # All topics must be from MAIN_TOPICS
    result_topics = {t["topic"] for t in result}
    assert result_topics == set(MAIN_TOPICS), f"Topics don't match main topics. Got: {result_topics}"
    
    print(f"[OK] Exactly 5 topics returned even with fewer input topics: {[t['topic'] for t in result]}")


if __name__ == "__main__":
    print("=" * 80)
    print("TESTING 5 TOPICS ENFORCEMENT")
    print("=" * 80)
    
    test_map_topic_to_main()
    test_enforce_five_topics()
    test_enforce_five_topics_with_fewer_topics()
    
    print("\n" + "=" * 80)
    print("[OK] ALL TESTS PASSED!")
    print("=" * 80)

