"""
Verify that the prompt includes topics data correctly.
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from backend.services.ai_prompts import SYSTEM_INSTRUCTION, build_user_prompt

# Load topics from database (using Flask app context)
from backend.app import create_app

app = create_app()
topics_data = None

with app.app_context():
    repo = app.extensions.get("repository")
    if repo:
        topics_raw = repo.get_topics(subject="Mathematics")
        
        # Format topics - prerequisite_topics is text[] array of topic names
        topics_data = []
        for topic in topics_raw:
            # prerequisite_topics is a text[] array containing topic names directly
            prerequisite_topics = topic.get("prerequisite_topics", [])
            if not isinstance(prerequisite_topics, list):
                prerequisite_topics = []
            
            topics_data.append({
                "name": topic.get("name", "Unknown"),
                "jamb_weight": topic.get("jamb_weight", 0.0),
                "prerequisites": prerequisite_topics  # Direct from prerequisite_topics text[] array
            })
        
        print(f"[OK] Loaded {len(topics_data)} topics from database")
        if topics_data:
            total_prereqs = sum(len(t.get("prerequisites", [])) for t in topics_data)
            print(f"[OK] Total prerequisites across all topics: {total_prereqs}")

# Sample quiz data
quiz_data = {
    "subject": "Mathematics",
    "total_questions": 15,
    "time_taken": 25.5,
    "questions_list": [
        {
            "id": 1,
            "topic": "Algebra",
            "student_answer": "B",
            "correct_answer": "A",
            "is_correct": False,
            "confidence": 2,
            "explanation": "I thought we needed to subtract 5 from both sides, but I made a sign error."
        }
    ]
}

# Build prompt
user_prompt = build_user_prompt(quiz_data, topics_data=topics_data)
full_prompt = f"{SYSTEM_INSTRUCTION}\n\n{user_prompt}\n\nRemember: Return ONLY valid JSON matching the required schema. No markdown, no code blocks, no explanations outside JSON."

# Save to file
with open("complete_prompt_with_topics.txt", "w", encoding="utf-8") as f:
    f.write(full_prompt)

print("[OK] Complete prompt generated with topics")
print(f"[OK] Prompt length: {len(full_prompt)} characters")
print(f"[OK] Topics included: {'Available Topics' in full_prompt}")
print(f"[OK] Topics JSON format correct: {'Number and Numeration' in full_prompt and '\"prerequisites\":' in full_prompt}")
print()
print("=" * 80)
print("TOPICS SECTION FROM PROMPT:")
print("=" * 80)

# Extract topics section
if "Available Topics" in full_prompt:
    start_idx = full_prompt.find("Available Topics")
    end_idx = full_prompt.find("Your Task:", start_idx)
    if end_idx > 0:
        topics_section = full_prompt[start_idx:end_idx]
        print(topics_section)
    else:
        print("Could not extract topics section")
else:
    print("Topics section not found")

print()
print("[OK] Complete prompt saved to: complete_prompt_with_topics.txt")

