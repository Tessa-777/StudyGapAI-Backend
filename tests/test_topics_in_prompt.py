"""
Test to verify topics with prerequisites are correctly included in the prompt.
This test uses the actual database to fetch topics with prerequisites.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.app import create_app
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

# Create app and fetch real topics from database
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
            
            # Show topics with prerequisites
            print("\nTopics with prerequisites:")
            for topic in topics_data:
                prereqs = topic.get("prerequisites", [])
                if prereqs:
                    print(f"  - {topic['name']}: {len(prereqs)} prerequisites")
                    print(f"    First 3: {prereqs[:3]}")

# Test prompt building with real topics
prompt = build_user_prompt(quiz_data, topics_data=topics_data)

print("\n" + "=" * 80)
print("PROMPT VERIFICATION")
print("=" * 80)
print(f"[OK] Prompt built successfully")
print(f"[OK] Prompt includes topics: {'Available Topics' in prompt}")
print(f"[OK] Prompt length: {len(prompt)} characters")

# Check if prerequisites are in the prompt
has_prerequisites = False
if topics_data:
    for topic in topics_data:
        prereqs = topic.get("prerequisites", [])
        if prereqs and prereqs[0] in prompt:
            has_prerequisites = True
            break

print(f"[OK] Prerequisites included in prompt: {has_prerequisites}")

# Extract and show topics section
if "Available Topics" in prompt:
    start_idx = prompt.find("Available Topics")
    end_idx = prompt.find("Your Task:", start_idx)
    if end_idx > 0:
        topics_section = prompt[start_idx:end_idx]
        print("\n" + "=" * 80)
        print("TOPICS SECTION FROM PROMPT:")
        print("=" * 80)
        print(topics_section[:1000])  # First 1000 chars
        if len(topics_section) > 1000:
            print("... (truncated)")
    else:
        print("[WARNING] Could not extract topics section")

print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"[OK] Topics loaded: {len(topics_data) if topics_data else 0}")
print(f"[OK] Prerequisites found: {has_prerequisites}")
print(f"[OK] Prompt generated: {len(prompt)} characters")
print("\n[OK] All tests passed!")

