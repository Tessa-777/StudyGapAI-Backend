"""
Generate the complete prompt that would be sent to Gemini for testing.
This replicates exactly what the backend would send.
"""

from backend.services.ai_prompts import SYSTEM_INSTRUCTION, build_user_prompt

# Sample quiz data - 15 questions with realistic responses
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
        },
        {
            "id": 2,
            "topic": "Algebra",
            "student_answer": "A",
            "correct_answer": "A",
            "is_correct": True,
            "confidence": 4,
            "explanation": "I solved it step by step and checked my work."
        },
        {
            "id": 3,
            "topic": "Geometry",
            "student_answer": "C",
            "correct_answer": "D",
            "is_correct": False,
            "confidence": 3,
            "explanation": "I used the wrong formula for the area of a triangle. I forgot to divide by 2."
        },
        {
            "id": 4,
            "topic": "Geometry",
            "student_answer": "D",
            "correct_answer": "D",
            "is_correct": True,
            "confidence": 5,
            "explanation": "I remembered the Pythagorean theorem correctly."
        },
        {
            "id": 5,
            "topic": "Trigonometry",
            "student_answer": "A",
            "correct_answer": "B",
            "is_correct": False,
            "confidence": 2,
            "explanation": "I confused sine with cosine. I don't really understand the unit circle."
        },
        {
            "id": 6,
            "topic": "Trigonometry",
            "student_answer": "C",
            "correct_answer": "C",
            "is_correct": True,
            "confidence": 4,
            "explanation": "I used the correct trigonometric identity."
        },
        {
            "id": 7,
            "topic": "Calculus",
            "student_answer": "B",
            "correct_answer": "A",
            "is_correct": False,
            "confidence": 1,
            "explanation": "I tried to differentiate but I'm not sure about the chain rule. I guessed."
        },
        {
            "id": 8,
            "topic": "Calculus",
            "student_answer": "D",
            "correct_answer": "D",
            "is_correct": True,
            "confidence": 3,
            "explanation": "I applied the power rule correctly."
        },
        {
            "id": 9,
            "topic": "Statistics",
            "student_answer": "A",
            "correct_answer": "A",
            "is_correct": True,
            "confidence": 5,
            "explanation": "I calculated the mean correctly by adding all values and dividing by the count."
        },
        {
            "id": 10,
            "topic": "Statistics",
            "student_answer": "B",
            "correct_answer": "C",
            "is_correct": False,
            "confidence": 2,
            "explanation": "I don't understand what median means. I just picked the middle number without sorting."
        },
        {
            "id": 11,
            "topic": "Number Theory",
            "student_answer": "C",
            "correct_answer": "C",
            "is_correct": True,
            "confidence": 4,
            "explanation": "I found the LCM correctly by listing multiples."
        },
        {
            "id": 12,
            "topic": "Number Theory",
            "student_answer": "A",
            "correct_answer": "B",
            "is_correct": False,
            "confidence": 3,
            "explanation": "I made a calculation error when finding the GCD. I forgot to check all factors."
        },
        {
            "id": 13,
            "topic": "Algebra",
            "student_answer": "B",
            "correct_answer": "B",
            "is_correct": True,
            "confidence": 4,
            "explanation": "I factored the quadratic equation correctly."
        },
        {
            "id": 14,
            "topic": "Geometry",
            "student_answer": "A",
            "correct_answer": "C",
            "is_correct": False,
            "confidence": 2,
            "explanation": "I don't understand similar triangles. I just compared the numbers without checking the ratios."
        },
        {
            "id": 15,
            "topic": "Trigonometry",
            "student_answer": "D",
            "correct_answer": "D",
            "is_correct": True,
            "confidence": 3,
            "explanation": "I used the correct angle addition formula."
        }
    ]
}

# Load topics data from all_topics.json
topics_data = None
try:
    import json
    from pathlib import Path
    topics_file = Path(__file__).parent / "all_topics.json"
    if topics_file.exists():
        with open(topics_file, "r", encoding="utf-8") as f:
            topics_raw = json.load(f)
            # Format topics to match expected structure
            topics_data = []
            topic_id_to_name = {t.get("id"): t.get("name") for t in topics_raw if t.get("id")}
            
            for topic in topics_raw:
                prerequisite_ids = topic.get("prerequisite_topic_ids", [])
                prerequisite_names = []
                
                # Resolve prerequisite IDs to names
                for prereq_id in prerequisite_ids:
                    prereq_name = topic_id_to_name.get(prereq_id)
                    if prereq_name:
                        prerequisite_names.append(prereq_name)
                
                topics_data.append({
                    "name": topic.get("name", "Unknown"),
                    "jamb_weight": topic.get("jamb_weight", 0.0),
                    "prerequisite_topic_ids": prerequisite_ids,
                    "prerequisite_names": prerequisite_names,
                    "prerequisites": prerequisite_names
                })
            
            print(f"[OK] Loaded {len(topics_data)} topics from all_topics.json")
    else:
        print("[WARNING] all_topics.json not found - topics will not be included in prompt")
except Exception as e:
    print(f"[WARNING] Failed to load topics: {e}")

# Build the user prompt with topics data
user_prompt = build_user_prompt(quiz_data, topics_data=topics_data)

# Combine system instruction and user prompt (exactly as done in ai_enhanced.py)
full_prompt = f"{SYSTEM_INSTRUCTION}\n\n{user_prompt}\n\nRemember: Return ONLY valid JSON matching the required schema. No markdown, no code blocks, no explanations outside JSON."

# Print the complete prompt
print("=" * 80)
print("COMPLETE PROMPT TO SEND TO GEMINI")
print("=" * 80)
print()
print(full_prompt)
print()
print("=" * 80)
print("END OF PROMPT")
print("=" * 80)

# Also save to file
with open("gemini_test_prompt.txt", "w", encoding="utf-8") as f:
    f.write(full_prompt)

print("\n[OK] Prompt also saved to: gemini_test_prompt.txt")
print("\nQuiz Statistics:")
print(f"   Total Questions: {quiz_data['total_questions']}")
correct = sum(1 for q in quiz_data['questions_list'] if q['is_correct'])
print(f"   Correct Answers: {correct}/{quiz_data['total_questions']} ({correct/quiz_data['total_questions']*100:.1f}%)")
avg_confidence = sum(q['confidence'] for q in quiz_data['questions_list']) / len(quiz_data['questions_list'])
print(f"   Average Confidence: {avg_confidence:.2f}/5")
print(f"   Time Taken: {quiz_data['time_taken']} minutes")
print(f"   Topics in quiz: {', '.join(set(q['topic'] for q in quiz_data['questions_list']))}")
if topics_data:
    print(f"   Topics data included: {len(topics_data)} topics with prerequisites")
else:
    print("   Topics data: Not included")

