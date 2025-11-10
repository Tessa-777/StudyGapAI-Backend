"""
Topic mapping utilities - map prerequisite topics to 5 main topics
"""
from typing import Dict, List, Any, Optional


# The 5 main topics that must be returned
MAIN_TOPICS = [
    "Number and Numeration",
    "Algebra",
    "Geometry and Trigonometry",
    "Calculus",
    "Statistics and Probability"
]


# Mapping of prerequisite topics to main topics
# This maps common prerequisite topic names to their main topic
TOPIC_MAPPING = {
    # Number and Numeration
    "number bases": "Number and Numeration",
    "fractions": "Number and Numeration",
    "decimals": "Number and Numeration",
    "approximations": "Number and Numeration",
    "percentages": "Number and Numeration",
    "simple interest": "Number and Numeration",
    "profit and loss": "Number and Numeration",
    "ratio and proportion": "Number and Numeration",
    "indices": "Number and Numeration",
    "logarithms": "Number and Numeration",
    "surds": "Number and Numeration",
    "set theory": "Number and Numeration",
    "venn diagrams": "Number and Numeration",
    "number system": "Number and Numeration",
    "number theory": "Number and Numeration",
    "number and numeration": "Number and Numeration",
    
    # Algebra
    "polynomials": "Algebra",
    "variations": "Algebra",
    "inequalities": "Algebra",
    "progressions": "Algebra",
    "binary operations": "Algebra",
    "matrices": "Algebra",
    "change of subject": "Algebra",
    "factor and remainder theorems": "Algebra",
    "factorization": "Algebra",
    "roots": "Algebra",
    "simultaneous equations": "Algebra",
    "graphs of polynomials": "Algebra",
    "direct variation": "Algebra",
    "inverse variation": "Algebra",
    "joint variation": "Algebra",
    "partial variation": "Algebra",
    "linear inequalities": "Algebra",
    "quadratic inequalities": "Algebra",
    "arithmetic progressions": "Algebra",
    "geometric progressions": "Algebra",
    "algebra": "Algebra",
    "equations": "Algebra",
    "linear equations": "Algebra",
    "quadratic equations": "Algebra",
    
    # Geometry and Trigonometry
    "properties of angles": "Geometry and Trigonometry",
    "properties of lines": "Geometry and Trigonometry",
    "polygons": "Geometry and Trigonometry",
    "circles": "Geometry and Trigonometry",
    "chords": "Geometry and Trigonometry",
    "geometric construction": "Geometry and Trigonometry",
    "perimeters": "Geometry and Trigonometry",
    "areas": "Geometry and Trigonometry",
    "surface areas": "Geometry and Trigonometry",
    "volumes": "Geometry and Trigonometry",
    "longitudes": "Geometry and Trigonometry",
    "latitudes": "Geometry and Trigonometry",
    "locus": "Geometry and Trigonometry",
    "midpoint": "Geometry and Trigonometry",
    "gradient": "Geometry and Trigonometry",
    "distance between points": "Geometry and Trigonometry",
    "equations of straight lines": "Geometry and Trigonometry",
    "trigonometrical ratios": "Geometry and Trigonometry",
    "angles of elevation": "Geometry and Trigonometry",
    "angles of depression": "Geometry and Trigonometry",
    "bearings": "Geometry and Trigonometry",
    "sine rule": "Geometry and Trigonometry",
    "cosine rule": "Geometry and Trigonometry",
    "geometry": "Geometry and Trigonometry",
    "trigonometry": "Geometry and Trigonometry",
    "coordinate geometry": "Geometry and Trigonometry",
    
    # Calculus
    "limit of a function": "Calculus",
    "differentiation": "Calculus",
    "integration": "Calculus",
    "rates of change": "Calculus",
    "maxima": "Calculus",
    "minima": "Calculus",
    "area under a curve": "Calculus",
    "calculus": "Calculus",
    "derivatives": "Calculus",
    "integrals": "Calculus",
    
    # Statistics and Probability
    "frequency distribution": "Statistics and Probability",
    "histogram": "Statistics and Probability",
    "bar chart": "Statistics and Probability",
    "pie chart": "Statistics and Probability",
    "mean": "Statistics and Probability",
    "median": "Statistics and Probability",
    "mode": "Statistics and Probability",
    "cumulative frequency": "Statistics and Probability",
    "range": "Statistics and Probability",
    "mean deviation": "Statistics and Probability",
    "variance": "Statistics and Probability",
    "standard deviation": "Statistics and Probability",
    "permutation": "Statistics and Probability",
    "combination": "Statistics and Probability",
    "experimental probability": "Statistics and Probability",
    "addition of probabilities": "Statistics and Probability",
    "multiplication of probabilities": "Statistics and Probability",
    "statistics": "Statistics and Probability",
    "probability": "Statistics and Probability",
}


def map_topic_to_main(topic_name: str) -> str:
    """
    Map a topic name (prerequisite or main) to one of the 5 main topics.
    
    Args:
        topic_name: Topic name from question or AI response
        
    Returns:
        One of the 5 main topic names
    """
    if not topic_name:
        return "Number and Numeration"  # Default
    
    # Clean topic name
    topic_clean = topic_name.strip()
    
    # Remove "Subject: " prefix if present
    if ":" in topic_clean:
        topic_clean = topic_clean.split(":")[-1].strip()
    
    topic_lower = topic_clean.lower()
    
    # Check if it's already a main topic
    for main_topic in MAIN_TOPICS:
        if topic_lower == main_topic.lower():
            return main_topic
    
    # Check mapping
    if topic_lower in TOPIC_MAPPING:
        return TOPIC_MAPPING[topic_lower]
    
    # Try partial matching
    for key, main_topic in TOPIC_MAPPING.items():
        if key in topic_lower or topic_lower in key:
            return main_topic
    
    # Default fallback based on common keywords
    if any(word in topic_lower for word in ["number", "numeration", "fraction", "decimal", "percentage", "ratio", "set"]):
        return "Number and Numeration"
    elif any(word in topic_lower for word in ["algebra", "equation", "polynomial", "inequality", "progression"]):
        return "Algebra"
    elif any(word in topic_lower for word in ["geometry", "trigonometry", "angle", "circle", "triangle", "coordinate"]):
        return "Geometry and Trigonometry"
    elif any(word in topic_lower for word in ["calculus", "differentiation", "integration", "derivative", "integral"]):
        return "Calculus"
    elif any(word in topic_lower for word in ["statistics", "probability", "mean", "median", "mode", "permutation", "combination"]):
        return "Statistics and Probability"
    
    # Ultimate fallback
    return "Number and Numeration"


def enforce_five_topics(topic_breakdown: List[Dict[str, Any]], questions_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enforce exactly 5 topics by aggregating all topics into the 5 main topics.
    
    Args:
        topic_breakdown: Topic breakdown from AI (may have more than 5)
        questions_list: List of all questions
        
    Returns:
        Topic breakdown with exactly 5 topics
    """
    from backend.utils.calculations import calculate_fluency_index, validate_topic_status
    
    # Initialize 5 main topics with empty data
    main_topics_data = {topic: {
        "topic": topic,
        "accuracy": 0.0,
        "fluency_index": 0.0,
        "status": "weak",
        "questions_attempted": 0,
        "severity": None,
        "dominant_error_type": None,
        "total_questions": 0,
        "correct_questions": 0,
        "confidences": []
    } for topic in MAIN_TOPICS}
    
    # Aggregate all topics from breakdown into main topics
    for topic_item in topic_breakdown:
        topic_name = topic_item.get("topic", "")
        main_topic = map_topic_to_main(topic_name)
        
        # Aggregate data
        main_data = main_topics_data[main_topic]
        main_data["total_questions"] += topic_item.get("questions_attempted", 0)
        main_data["questions_attempted"] += topic_item.get("questions_attempted", 0)
        
        # For accuracy, we need to recalculate from questions
        # But we can use weighted average if we have the data
        topic_accuracy = topic_item.get("accuracy", 0.0)
        topic_count = topic_item.get("questions_attempted", 0)
        if topic_count > 0:
            # Weighted average accuracy
            current_total = main_data["total_questions"]
            if current_total > 0:
                # Weighted average
                main_data["accuracy"] = (
                    (main_data["accuracy"] * (current_total - topic_count) + topic_accuracy * topic_count) 
                    / current_total
                )
            else:
                main_data["accuracy"] = topic_accuracy
        
        # Aggregate confidences (we'll recalculate from questions anyway)
        topic_confidence = topic_item.get("avg_confidence", 3.0)
        if topic_count > 0:
            main_data["confidences"].extend([topic_confidence] * topic_count)
    
    # Recalculate from questions for accuracy
    for main_topic in MAIN_TOPICS:
        main_data = main_topics_data[main_topic]
        
        # Find all questions that map to this main topic
        topic_questions = []
        for q in questions_list:
            q_topic = q.get("topic", "")
            mapped_topic = map_topic_to_main(q_topic)
            if mapped_topic == main_topic:
                topic_questions.append(q)
        
        if topic_questions:
            total = len(topic_questions)
            correct = sum(1 for q in topic_questions if q.get("is_correct", False))
            accuracy = (correct / total * 100.0) if total > 0 else 0.0
            
            confidences = [q.get("confidence", 3) for q in topic_questions]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 3.0
            
            fluency_index = calculate_fluency_index(accuracy, avg_confidence)
            fluency_index = max(0.0, min(100.0, fluency_index))
            
            status = validate_topic_status({
                "fluency_index": fluency_index,
                "accuracy": accuracy
            })
            
            severity = None
            if status == "weak":
                severity = "critical" if accuracy < 40 else "moderate"
            elif status == "developing":
                severity = "moderate"
            
            # Update main topic data
            main_data["topic"] = main_topic
            main_data["accuracy"] = round(accuracy, 2)
            main_data["fluency_index"] = round(fluency_index, 2)
            main_data["status"] = status
            main_data["questions_attempted"] = total
            main_data["severity"] = severity
            main_data["dominant_error_type"] = "knowledge_gap" if status == "weak" else None
    
    # Build final breakdown with exactly 5 topics
    final_breakdown = []
    for main_topic in MAIN_TOPICS:
        main_data = main_topics_data[main_topic]
        final_breakdown.append({
            "topic": main_data["topic"],
            "accuracy": main_data["accuracy"],
            "fluency_index": main_data["fluency_index"],
            "status": main_data["status"],
            "questions_attempted": main_data["questions_attempted"],
            "severity": main_data["severity"],
            "dominant_error_type": main_data["dominant_error_type"]
        })
    
    return final_breakdown

