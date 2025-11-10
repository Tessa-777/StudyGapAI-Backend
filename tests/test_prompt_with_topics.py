"""
Test script to verify the prompt includes topics data correctly.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.services.ai_prompts import build_user_prompt

# Sample quiz data
quiz_data = {
    'subject': 'Mathematics',
    'total_questions': 15,
    'time_taken': 25.5,
    'questions_list': [
        {
            'topic': 'Algebra',
            'student_answer': 'A',
            'correct_answer': 'A',
            'is_correct': True,
            'confidence': 4,
            'explanation': 'Test explanation'
        }
    ]
}

# Sample topics data (matching format from all_topics.json)
topics = [
    {
        'name': 'Number and Numeration',
        'jamb_weight': 0.15,
        'prerequisites': []
    },
    {
        'name': 'Algebra',
        'jamb_weight': 0.19,
        'prerequisites': []
    },
    {
        'name': 'Geometry and Trigonometry',
        'jamb_weight': 0.17,
        'prerequisites': []
    },
    {
        'name': 'Calculus',
        'jamb_weight': 0.11,
        'prerequisites': []
    },
    {
        'name': 'Statistics and Probability',
        'jamb_weight': 0.15,
        'prerequisites': []
    }
]

# Test prompt building
prompt = build_user_prompt(quiz_data, topics_data=topics)

print("[OK] Prompt built successfully")
print(f"[OK] Prompt includes topics: {'Available Topics' in prompt}")
print(f"[OK] Prompt length: {len(prompt)} characters")
print(f"[OK] Topics JSON in prompt: {'Number and Numeration' in prompt}")
print()
print("=" * 80)
print("PROMPT PREVIEW (first 500 chars):")
print("=" * 80)
print(prompt[:500])
print("...")
print()
print("=" * 80)
print("TOPICS SECTION:")
print("=" * 80)
if "Available Topics" in prompt:
    # Extract topics section
    start_idx = prompt.find("Available Topics")
    end_idx = prompt.find("Your Task:", start_idx)
    if end_idx > 0:
        print(prompt[start_idx:end_idx])
    else:
        print("Topics section found but couldn't extract")
else:
    print("Topics section not found in prompt")

