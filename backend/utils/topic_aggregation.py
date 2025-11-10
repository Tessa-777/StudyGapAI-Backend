"""
Topic aggregation utilities - aggregate prerequisite topics into parent topics
"""
from typing import Dict, Any, List, Optional
from collections import defaultdict


def map_prerequisites_to_parents(topics_data: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Create a mapping from prerequisite topic names to their parent topic names.
    
    Args:
        topics_data: List of topics with prerequisite_topics field
        
    Returns:
        Dictionary mapping prerequisite topic name -> parent topic name
    """
    prerequisite_to_parent = {}
    
    for topic in topics_data:
        parent_name = topic.get("name", "")
        prerequisites = topic.get("prerequisites", [])
        
        if not isinstance(prerequisites, list):
            prerequisites = []
        
        for prereq in prerequisites:
            if isinstance(prereq, str) and prereq.strip():
                prerequisite_to_parent[prereq.strip().lower()] = parent_name
    
    return prerequisite_to_parent


def map_question_to_parent_topic(
    question_topic: str,
    main_topic_names: Dict[str, str],
    prereq_to_parent: Dict[str, str]
) -> Optional[str]:
    """
    Map a question's topic (which could be a prerequisite) to its parent topic.
    
    Args:
        question_topic: The topic name from the question
        main_topic_names: Dict of main topic names (lowercase -> actual name)
        prereq_to_parent: Dict mapping prerequisites to parent topics
        
    Returns:
        Parent topic name if found, None otherwise
    """
    # Clean the topic name
    topic_clean = question_topic.strip()
    if ":" in topic_clean:
        topic_clean = topic_clean.split(":")[-1].strip()
    
    topic_lower = topic_clean.lower()
    
    # Check if it's already a main topic
    if topic_lower in main_topic_names:
        return main_topic_names[topic_lower]
    
    # Check if it's a prerequisite
    if topic_lower in prereq_to_parent:
        return prereq_to_parent[topic_lower]
    
    # Try fuzzy matching with prerequisites
    for prereq, parent in prereq_to_parent.items():
        if topic_lower in prereq or prereq in topic_lower:
            return parent
    
    # Try fuzzy matching with main topics
    for main_lower, main_name in main_topic_names.items():
        if topic_lower in main_lower or main_lower in topic_lower:
            return main_name
    
    return None


def aggregate_topics_by_parent(
    topic_breakdown: List[Dict[str, Any]],
    questions_list: List[Dict[str, Any]],
    topics_data: Optional[List[Dict[str, Any]]] = None,
    subject: str = "Mathematics"
) -> List[Dict[str, Any]]:
    """
    Aggregate prerequisite topics into their parent topics.
    Maps ALL questions directly to parent topics and returns ALL main topics.
    
    Args:
        topic_breakdown: Topic breakdown from AI (may contain prerequisites) - used for error types
        questions_list: List of all questions
        topics_data: List of main topics from database (with prerequisites)
        subject: Subject name (will be removed from topic names in output)
        
    Returns:
        Aggregated topic breakdown with only main topics, all questions mapped correctly
    """
    if not topics_data:
        # If no topics data, return original breakdown but clean topic names
        cleaned_breakdown = []
        for topic_item in topic_breakdown:
            cleaned = topic_item.copy()
            topic_name = cleaned.get("topic", "")
            if ":" in topic_name:
                cleaned["topic"] = topic_name.split(":")[-1].strip()
            cleaned_breakdown.append(cleaned)
        return cleaned_breakdown
    
    # Create mapping from prerequisites to parents
    prereq_to_parent = map_prerequisites_to_parents(topics_data)
    
    # Get main topic names
    main_topic_names = {t.get("name", "").lower(): t.get("name", "") for t in topics_data}
    
    # Aggregate data by parent topic - map ALL questions directly
    aggregated_data = defaultdict(lambda: {
        "questions": [],
        "correct_count": 0,
        "total_count": 0,
        "confidences": [],
        "error_types": defaultdict(int),
        "topics_seen": set()
    })
    
    # Map ALL questions directly to parent topics
    for q in questions_list:
        question_topic = q.get("topic", "")
        if not question_topic or not question_topic.strip():
            continue
        
        parent_topic = map_question_to_parent_topic(
            question_topic,
            main_topic_names,
            prereq_to_parent
        )
        
        if parent_topic:
            parent_lower = parent_topic.lower()
            # Only add if not already added (avoid duplicates)
            if q not in aggregated_data[parent_lower]["questions"]:
                aggregated_data[parent_lower]["questions"].append(q)
                aggregated_data[parent_lower]["correct_count"] += 1 if q.get("is_correct", False) else 0
                aggregated_data[parent_lower]["total_count"] += 1
                aggregated_data[parent_lower]["confidences"].append(q.get("confidence", 3))
                aggregated_data[parent_lower]["topics_seen"].add(question_topic.strip())
    
    # Also process AI's topic breakdown for error types and additional insights
    for topic_item in topic_breakdown:
        topic_name = topic_item.get("topic", "")
        
        # Extract base topic name
        if ":" in topic_name:
            base_topic = topic_name.split(":")[-1].strip()
        else:
            base_topic = topic_name.strip()
        
        base_topic_lower = base_topic.lower()
        
        # Find parent topic
        parent_topic = map_question_to_parent_topic(
            base_topic,
            main_topic_names,
            prereq_to_parent
        )
        
        if parent_topic:
            parent_lower = parent_topic.lower()
            
            # Aggregate error types from AI breakdown
            if topic_item.get("dominant_error_type"):
                error_type = topic_item.get("dominant_error_type")
                # Count questions that match this topic
                matching_questions = [
                    q for q in questions_list
                    if map_question_to_parent_topic(q.get("topic", ""), main_topic_names, prereq_to_parent) == parent_topic
                ]
                aggregated_data[parent_lower]["error_types"][error_type] += len(matching_questions)
    
    # Build final topic breakdown with ALL main topics (even if 0 questions)
    from backend.utils.calculations import calculate_fluency_index, validate_topic_status
    
    final_breakdown = []
    
    # Process ALL main topics (sorted for consistency)
    sorted_topics = sorted(main_topic_names.items(), key=lambda x: x[1])
    
    for main_topic_lower, main_topic_name in sorted_topics:
        agg_data = aggregated_data[main_topic_lower]
        
        # Calculate aggregated metrics
        total_questions = agg_data["total_count"]
        correct_answers = agg_data["correct_count"]
        
        # Calculate accuracy (0% if no questions)
        accuracy = (correct_answers / total_questions * 100.0) if total_questions > 0 else 0.0
        
        confidences = agg_data["confidences"]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 3.0
        
        fluency_index = calculate_fluency_index(accuracy, avg_confidence)
        fluency_index = max(0.0, min(100.0, fluency_index))
        
        # Determine status
        status = validate_topic_status({
            "fluency_index": fluency_index,
            "accuracy": accuracy
        })
        
        # Determine severity
        severity = None
        if status == "weak":
            severity = "critical" if accuracy < 40 else "moderate"
        elif status == "developing":
            severity = "moderate"
        
        # Determine dominant error type
        dominant_error_type = None
        if agg_data["error_types"]:
            dominant_error_type = max(agg_data["error_types"].items(), key=lambda x: x[1])[0]
        
        # Build topic entry - NO "Subject: " prefix, just topic name
        topic_entry = {
            "topic": main_topic_name,  # Just the topic name, no "Mathematics: " prefix
            "accuracy": round(accuracy, 2),
            "fluency_index": round(fluency_index, 2),
            "status": status,
            "questions_attempted": total_questions,  # Always include, even if 0
            "severity": severity,
        }
        
        if dominant_error_type:
            topic_entry["dominant_error_type"] = dominant_error_type
        
        final_breakdown.append(topic_entry)
    
    return final_breakdown
