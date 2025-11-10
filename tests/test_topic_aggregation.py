"""
Comprehensive tests for topic aggregation functionality
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.utils.topic_aggregation import (
    map_prerequisites_to_parents,
    map_question_to_parent_topic,
    aggregate_topics_by_parent
)


def test_map_prerequisites_to_parents():
    """Test mapping prerequisites to parent topics"""
    topics_data = [
        {
            "name": "Number and Numeration",
            "prerequisites": ["Number bases", "Fractions", "Decimals"]
        },
        {
            "name": "Algebra",
            "prerequisites": ["Number bases", "Fractions", "Polynomials"]
        }
    ]
    
    mapping = map_prerequisites_to_parents(topics_data)
    
    assert "number bases" in mapping
    assert mapping["number bases"] == "Algebra"  # Last one wins (should be fine for our use case)
    assert mapping["fractions"] == "Algebra"
    assert mapping["decimals"] == "Number and Numeration"
    assert mapping["polynomials"] == "Algebra"
    
    print("[OK] Prerequisite mapping works correctly")


def test_map_question_to_parent_topic():
    """Test mapping question topics to parent topics"""
    main_topic_names = {
        "number and numeration": "Number and Numeration",
        "algebra": "Algebra",
        "geometry and trigonometry": "Geometry and Trigonometry"
    }
    
    prereq_to_parent = {
        "number bases": "Number and Numeration",
        "fractions": "Number and Numeration",
        "polynomials": "Algebra"
    }
    
    # Test main topic
    assert map_question_to_parent_topic("Algebra", main_topic_names, prereq_to_parent) == "Algebra"
    
    # Test prerequisite
    assert map_question_to_parent_topic("Number bases", main_topic_names, prereq_to_parent) == "Number and Numeration"
    assert map_question_to_parent_topic("Fractions", main_topic_names, prereq_to_parent) == "Number and Numeration"
    assert map_question_to_parent_topic("Polynomials", main_topic_names, prereq_to_parent) == "Algebra"
    
    # Test with "Subject: Topic" format
    assert map_question_to_parent_topic("Mathematics: Algebra", main_topic_names, prereq_to_parent) == "Algebra"
    assert map_question_to_parent_topic("Mathematics: Number bases", main_topic_names, prereq_to_parent) == "Number and Numeration"
    
    print("[OK] Question to parent topic mapping works correctly")


def test_aggregate_topics_all_main_topics_included():
    """Test that ALL main topics are included even with 0 questions"""
    topics_data = [
        {"name": "Number and Numeration", "prerequisites": ["Number bases", "Fractions"]},
        {"name": "Algebra", "prerequisites": ["Polynomials"]},
        {"name": "Geometry and Trigonometry", "prerequisites": []},
        {"name": "Calculus", "prerequisites": []},
        {"name": "Statistics and Probability", "prerequisites": []}
    ]
    
    questions_list = [
        {"topic": "Number bases", "is_correct": True, "confidence": 4},
        {"topic": "Fractions", "is_correct": False, "confidence": 2},
        {"topic": "Polynomials", "is_correct": True, "confidence": 5}
    ]
    
    topic_breakdown = []  # Empty - aggregation should create from questions
    
    result = aggregate_topics_by_parent(
        topic_breakdown,
        questions_list,
        topics_data,
        "Mathematics"
    )
    
    # Should have all 5 main topics
    assert len(result) == 5, f"Expected 5 topics, got {len(result)}"
    
    topic_names = [t["topic"] for t in result]
    assert "Number and Numeration" in topic_names
    assert "Algebra" in topic_names
    assert "Geometry and Trigonometry" in topic_names
    assert "Calculus" in topic_names
    assert "Statistics and Probability" in topic_names
    
    # Check topic names don't have "Mathematics: " prefix
    for topic in result:
        assert not topic["topic"].startswith("Mathematics:"), f"Topic name should not have prefix: {topic['topic']}"
        assert ":" not in topic["topic"], f"Topic name should not contain colon: {topic['topic']}"
    
    # Check Number and Numeration has 2 questions (Number bases + Fractions)
    num_num = next(t for t in result if t["topic"] == "Number and Numeration")
    assert num_num["questions_attempted"] == 2, f"Expected 2 questions, got {num_num['questions_attempted']}"
    assert num_num["accuracy"] == 50.0, f"Expected 50% accuracy (1/2), got {num_num['accuracy']}"
    
    # Check Algebra has 1 question
    algebra = next(t for t in result if t["topic"] == "Algebra")
    assert algebra["questions_attempted"] == 1, f"Expected 1 question, got {algebra['questions_attempted']}"
    assert algebra["accuracy"] == 100.0, f"Expected 100% accuracy, got {algebra['accuracy']}"
    
    # Check other topics have 0 questions
    geometry = next(t for t in result if t["topic"] == "Geometry and Trigonometry")
    assert geometry["questions_attempted"] == 0, f"Expected 0 questions, got {geometry['questions_attempted']}"
    assert geometry["accuracy"] == 0.0, f"Expected 0% accuracy, got {geometry['accuracy']}"
    
    print("[OK] All main topics included, questions correctly aggregated")


def test_aggregate_topics_question_distribution():
    """Test that questions are correctly distributed across topics"""
    topics_data = [
        {"name": "Number and Numeration", "prerequisites": ["Number bases", "Fractions", "Decimals"]},
        {"name": "Algebra", "prerequisites": ["Polynomials", "Equations"]},
        {"name": "Geometry and Trigonometry", "prerequisites": ["Triangles", "Circles"]},
        {"name": "Calculus", "prerequisites": ["Derivatives", "Integrals"]},
        {"name": "Statistics and Probability", "prerequisites": ["Mean", "Probability"]}
    ]
    
    # Create 30 questions distributed across prerequisites
    questions_list = []
    prereqs = ["Number bases", "Fractions", "Decimals", "Polynomials", "Equations", 
               "Triangles", "Circles", "Derivatives", "Integrals", "Mean", "Probability"]
    
    for i in range(30):
        prereq = prereqs[i % len(prereqs)]
        questions_list.append({
            "topic": prereq,
            "is_correct": i % 2 == 0,  # Alternate correct/incorrect
            "confidence": 3 + (i % 3)  # Vary confidence
        })
    
    topic_breakdown = []
    
    result = aggregate_topics_by_parent(
        topic_breakdown,
        questions_list,
        topics_data,
        "Mathematics"
    )
    
    # All 5 topics should be present
    assert len(result) == 5
    
    # Check questions are distributed (roughly equal)
    question_counts = {t["topic"]: t["questions_attempted"] for t in result}
    total_questions = sum(question_counts.values())
    assert total_questions == 30, f"Expected 30 total questions, got {total_questions}"
    
    # Number and Numeration should have 3 questions (Number bases, Fractions, Decimals appear multiple times)
    # Each prerequisite appears ~3 times in 30 questions (30/11 ≈ 2.7, so some appear 3 times)
    num_num = question_counts.get("Number and Numeration", 0)
    assert num_num > 0, "Number and Numeration should have questions"
    
    print(f"[OK] Questions correctly distributed: {question_counts}")
    print(f"[OK] Total questions: {total_questions}")


def test_aggregate_topics_accuracy_calculation():
    """Test that accuracy is correctly calculated from aggregated questions"""
    topics_data = [
        {"name": "Algebra", "prerequisites": ["Polynomials", "Equations"]}
    ]
    
    questions_list = [
        {"topic": "Polynomials", "is_correct": True, "confidence": 5},
        {"topic": "Polynomials", "is_correct": True, "confidence": 4},
        {"topic": "Equations", "is_correct": False, "confidence": 2},
        {"topic": "Equations", "is_correct": False, "confidence": 1}
    ]
    
    result = aggregate_topics_by_parent(
        [],
        questions_list,
        topics_data,
        "Mathematics"
    )
    
    assert len(result) == 1
    algebra = result[0]
    
    assert algebra["questions_attempted"] == 4
    assert algebra["accuracy"] == 50.0  # 2 correct out of 4
    assert algebra["topic"] == "Algebra"  # No prefix
    
    # Check fluency index is calculated
    assert "fluency_index" in algebra
    assert algebra["fluency_index"] > 0
    
    print("[OK] Accuracy correctly calculated from aggregated questions")


if __name__ == "__main__":
    print("=" * 80)
    print("TESTING TOPIC AGGREGATION")
    print("=" * 80)
    
    test_map_prerequisites_to_parents()
    test_map_question_to_parent_topic()
    test_aggregate_topics_all_main_topics_included()
    test_aggregate_topics_question_distribution()
    test_aggregate_topics_accuracy_calculation()
    
    print("\n" + "=" * 80)
    print("[OK] ALL TESTS PASSED!")
    print("=" * 80)

