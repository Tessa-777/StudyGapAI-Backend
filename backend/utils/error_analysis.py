"""
Error analysis utilities - classify questions into error types
"""
from typing import Dict, Any, List


def classify_error_type(question: Dict[str, Any]) -> str:
    """
    Classify a question's error type based on explanation, confidence, and correctness.
    
    Args:
        question: Question dictionary with is_correct, explanation, confidence
        
    Returns:
        Error type: conceptual_gap, procedural_error, careless_mistake, knowledge_gap, misinterpretation
        Defaults to knowledge_gap if classification is unclear
    """
    if question.get("is_correct", False):
        # Correct answers don't have error types
        return None
    
    explanation = question.get("explanation", "").lower()
    confidence = question.get("confidence", 3)
    
    # Keywords for each error type
    conceptual_keywords = ["concept", "understand", "why", "reasoning", "logic", "fundamental", "principle", "theory"]
    procedural_keywords = ["step", "method", "process", "procedure", "formula", "calculation", "solve", "approach"]
    careless_keywords = ["mistake", "error", "wrong sign", "forgot", "missed", "accident", "careless", "silly"]
    knowledge_keywords = ["don't know", "never learned", "unfamiliar", "haven't studied", "missing", "lack"]
    misinterpretation_keywords = ["misread", "misunderstood", "confused", "thought", "assumed", "interpret"]
    
    explanation_lower = explanation.lower()
    
    # Check for misinterpretation (often explicit)
    if any(keyword in explanation_lower for keyword in misinterpretation_keywords):
        return "misinterpretation"
    
    # Check for knowledge gap (explicit lack of knowledge)
    if any(keyword in explanation_lower for keyword in knowledge_keywords):
        return "knowledge_gap"
    
    # Check for careless mistake (high confidence but wrong answer)
    if confidence >= 4 and any(keyword in explanation_lower for keyword in careless_keywords):
        return "careless_mistake"
    
    # Check for conceptual gap (understanding issues)
    if any(keyword in explanation_lower for keyword in conceptual_keywords):
        return "conceptual_gap"
    
    # Check for procedural error (method/process issues)
    if any(keyword in explanation_lower for keyword in procedural_keywords):
        return "procedural_error"
    
    # Default classification based on confidence and explanation length
    # If no clear match, default to knowledge_gap (most common error type)
    if confidence >= 4:
        # High confidence but wrong = likely careless mistake
        return "careless_mistake"
    elif len(explanation) < 20:
        # Very short explanation = likely knowledge gap
        return "knowledge_gap"
    elif "step" in explanation_lower or "calculate" in explanation_lower:
        # Mentions steps/calculations = procedural error
        return "procedural_error"
    else:
        # Default to knowledge_gap if unclear (most common error type)
        return "knowledge_gap"


def calculate_error_distribution(questions_list: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate error distribution from questions.
    
    Args:
        questions_list: List of question dictionaries
        
    Returns:
        Dictionary with error type counts
    """
    error_distribution = {
        "conceptual_gap": 0,
        "procedural_error": 0,
        "careless_mistake": 0,
        "knowledge_gap": 0,
        "misinterpretation": 0
    }
    
    incorrect_count = 0
    for q in questions_list:
        if not q.get("is_correct", False):
            incorrect_count += 1
            error_type = classify_error_type(q)
            if error_type:
                error_distribution[error_type] = error_distribution.get(error_type, 0) + 1
            else:
                # Fallback: if classification returns None, default to knowledge_gap
                error_distribution["knowledge_gap"] = error_distribution.get("knowledge_gap", 0) + 1
    
    # If no errors were classified (all returned None or no incorrect answers),
    # or if classification didn't work well, ensure we have data
    # Default case: if classification is unsatisfactory, classify everything as knowledge_gap
    if incorrect_count > 0 and not any(error_distribution.values()):
        # All classifications failed - default everything to knowledge_gap
        error_distribution["knowledge_gap"] = incorrect_count
    
    return error_distribution

