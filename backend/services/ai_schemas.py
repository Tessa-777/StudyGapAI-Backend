"""
JSON Schema definitions for Gemini structured output
Based on AI SE Prompt Documentation.md
"""

# Complete response schema for Gemini structured output
RESPONSE_SCHEMA = {
    "type": "object",
    "required": [
        "overall_performance",
        "topic_breakdown",
        "root_cause_analysis",
        "predicted_jamb_score",
        "study_plan",
        "recommendations",
        "analysis_summary"
    ],
    "properties": {
        "analysis_summary": {
            "type": "string",
            "description": "A concise text summary (2-4 sentences) written in SECOND PERSON ('You exhibit...', 'Your performance shows...') highlighting root causes, cognitive patterns, and foundational weaknesses. This will be displayed directly to the student, so use 'you/your' instead of 'the student/student's'. Should be brief and suitable for frontend display."
        },
        "overall_performance": {
            "type": "object",
            "required": ["accuracy", "total_questions", "correct_answers", "avg_confidence", "time_per_question"],
            "properties": {
                "accuracy": {"type": "number"},
                "total_questions": {"type": "integer"},
                "correct_answers": {"type": "integer"},
                "avg_confidence": {"type": "number"},
                "time_per_question": {"type": "number"}
            }
        },
        "topic_breakdown": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["topic", "accuracy", "fluency_index", "status", "questions_attempted"],
                "properties": {
                    "topic": {"type": "string"},
                    "accuracy": {"type": "number"},
                    "fluency_index": {"type": "number"},
                    "status": {"type": "string", "enum": ["weak", "developing", "strong"]},
                    "questions_attempted": {"type": "integer"},
                    "severity": {"type": "string", "enum": ["critical", "moderate", "mild"]},
                    "dominant_error_type": {"type": "string"}
                }
            }
        },
        "root_cause_analysis": {
            "type": "object",
            "required": ["primary_weakness", "error_distribution"],
            "properties": {
                "primary_weakness": {
                    "type": "string",
                    "enum": ["conceptual_gap", "procedural_error", "careless_mistake", "knowledge_gap", "misinterpretation"]
                },
                "error_distribution": {
                    "type": "object",
                    "properties": {
                        "conceptual_gap": {"type": "integer"},
                        "procedural_error": {"type": "integer"},
                        "careless_mistake": {"type": "integer"},
                        "knowledge_gap": {"type": "integer"},
                        "misinterpretation": {"type": "integer"}
                    }
                }
            }
        },
        "predicted_jamb_score": {
            "type": "object",
            "required": ["score", "confidence_interval"],
            "properties": {
                "score": {"type": "integer", "minimum": 0, "maximum": 400},
                "confidence_interval": {"type": "string"}
            }
        },
        "study_plan": {
            "type": "object",
            "required": ["weekly_schedule"],
            "properties": {
                "weekly_schedule": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["week", "focus", "study_hours", "key_activities"],
                        "properties": {
                            "week": {"type": "integer", "minimum": 1, "maximum": 6},
                            "focus": {"type": "string"},
                            "study_hours": {"type": "integer"},
                            "key_activities": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        }
                    }
                }
            }
        },
        "recommendations": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["priority", "category", "action", "rationale"],
                "properties": {
                    "priority": {"type": "integer"},
                    "category": {"type": "string"},
                    "action": {"type": "string"},
                    "rationale": {"type": "string"}
                }
            }
        }
    }
}

# Valid error types (Decision 6: Option A - Strict validation)
VALID_ERROR_TYPES = {
    "conceptual_gap",
    "procedural_error",
    "careless_mistake",
    "knowledge_gap",
    "misinterpretation"
}

# Valid topic statuses
VALID_TOPIC_STATUSES = {"weak", "developing", "strong"}

# Valid severity levels
VALID_SEVERITY_LEVELS = {"critical", "moderate", "mild", None}

