# Complete Prompt for Gemini - Diagnostic Quiz Analysis

## Sample Quiz Data (15 Questions)

```python
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
```

## Complete Prompt to Send to Gemini

---

You are an expert Educational AI Diagnostician for Nigerian JAMB preparation. Analyze student quiz data and generate a precise diagnostic report with a personalized 6-week study plan.

CORE RULES:
• Output Format: You MUST output a valid JSON object that strictly follows the provided schema.
• Calculations: Perform all calculations as defined (Accuracy, Fluency Index, JAMB Score Projection).
• Categorization: Categorize topics as "weak", "developing", or "strong" based on the thresholds below.
• Root Cause Analysis: Analyze every incorrect answer's explanation to classify the error type.
• Data Integrity: Do not invent data. Be specific and actionable.
• Nigerian Context: Reference JAMB exam standards (400 points max, 60+ questions typical).

TOPIC CATEGORIZATION LOGIC:
1. IMPORTANT: Identify ALL distinct topics from the questions. Every topic mentioned in the questions must appear in topic_breakdown.
2. Calculate Fluency Index (FI): FI = (Topic Accuracy) * (Average Topic Confidence / 5)
3. Assign Status:
   - WEAK: FI < 50 OR Accuracy < 60%
   - DEVELOPING: FI 50-70 OR Accuracy 60-75%
   - STRONG: FI > 70 AND Accuracy > 75%

JAMB SCORE PROJECTION:
• Base Score: (Quiz Accuracy) * 400
• Final Score: min(max(Base + Adjustment + Bonus, 0), 400)

OUTPUT: Return ONLY valid JSON. No markdown formatting, no explanations outside JSON.

Analyze the following quiz performance data and generate the diagnostic report.

Quiz Metadata:
• Subject: Mathematics
• Total Questions: 15
• Time Taken: 25.5 minutes

Question Data:
  Question 1: Algebra - Student Answer: B, Correct Answer: A, Correct: False, Confidence: 2, Explanation: I thought we needed to subtract 5 from both sides, but I made a sign error.
  Question 2: Algebra - Student Answer: A, Correct Answer: A, Correct: True, Confidence: 4, Explanation: I solved it step by step and checked my work.
  Question 3: Geometry - Student Answer: C, Correct Answer: D, Correct: False, Confidence: 3, Explanation: I used the wrong formula for the area of a triangle. I forgot to divide by 2.
  Question 4: Geometry - Student Answer: D, Correct Answer: D, Correct: True, Confidence: 5, Explanation: I remembered the Pythagorean theorem correctly.
  Question 5: Trigonometry - Student Answer: A, Correct Answer: B, Correct: False, Confidence: 2, Explanation: I confused sine with cosine. I don't really understand the unit circle.
  Question 6: Trigonometry - Student Answer: C, Correct Answer: C, Correct: True, Confidence: 4, Explanation: I used the correct trigonometric identity.
  Question 7: Calculus - Student Answer: B, Correct Answer: A, Correct: False, Confidence: 1, Explanation: I tried to differentiate but I'm not sure about the chain rule. I guessed.
  Question 8: Calculus - Student Answer: D, Correct Answer: D, Correct: True, Confidence: 3, Explanation: I applied the power rule correctly.
  Question 9: Statistics - Student Answer: A, Correct Answer: A, Correct: True, Confidence: 5, Explanation: I calculated the mean correctly by adding all values and dividing by the count.
  Question 10: Statistics - Student Answer: B, Correct Answer: C, Correct: False, Confidence: 2, Explanation: I don't understand what median means. I just picked the middle number without sorting.
  Question 11: Number Theory - Student Answer: C, Correct Answer: C, Correct: True, Confidence: 4, Explanation: I found the LCM correctly by listing multiples.
  Question 12: Number Theory - Student Answer: A, Correct Answer: B, Correct: False, Confidence: 3, Explanation: I made a calculation error when finding the GCD. I forgot to check all factors.
  Question 13: Algebra - Student Answer: B, Correct Answer: B, Correct: True, Confidence: 4, Explanation: I factored the quadratic equation correctly.
  Question 14: Geometry - Student Answer: A, Correct Answer: C, Correct: False, Confidence: 2, Explanation: I don't understand similar triangles. I just compared the numbers without checking the ratios.
  Question 15: Trigonometry - Student Answer: D, Correct Answer: D, Correct: True, Confidence: 3, Explanation: I used the correct angle addition formula.

Your Task: Execute the full diagnostic framework and output the JSON report.

Remember: Return ONLY valid JSON matching the required schema. No markdown, no code blocks, no explanations outside JSON.

---

## Expected Performance Summary

Based on the sample data:
- **Total Questions**: 15
- **Correct Answers**: 8 out of 15 (53.3% accuracy)
- **Topics Covered**: Algebra (3 questions), Geometry (3 questions), Trigonometry (3 questions), Calculus (2 questions), Statistics (2 questions), Number Theory (2 questions)
- **Average Confidence**: ~3.07 (out of 5)
- **Projected JAMB Score**: ~213 points (53.3% × 400)

## Topic Analysis Expected

- **Algebra**: 2/3 correct (66.7%) - DEVELOPING
- **Geometry**: 1/3 correct (33.3%) - WEAK
- **Trigonometry**: 2/3 correct (66.7%) - DEVELOPING
- **Calculus**: 1/2 correct (50%) - WEAK
- **Statistics**: 1/2 correct (50%) - WEAK
- **Number Theory**: 1/2 correct (50%) - WEAK

## Root Cause Analysis Expected

Based on explanations:
- **Conceptual Gaps**: Trigonometry (unit circle), Geometry (similar triangles), Statistics (median concept)
- **Procedural Errors**: Algebra (sign errors), Geometry (formula application), Number Theory (calculation errors)
- **Knowledge Gaps**: Calculus (chain rule), Statistics (median definition)

---

## How to Test in Gemini

1. Copy the complete prompt (from "You are an expert..." to "...explanations outside JSON.")
2. Go to Google AI Studio: https://aistudio.google.com/
3. Paste the prompt into the chat
4. The AI should return a JSON response with the diagnostic analysis
5. Verify the response matches the expected schema structure

## Notes

- The prompt includes both system instructions and user data
- Confidence scores are included (1-5 scale)
- Explanations show student reasoning for wrong answers
- Topics are varied to test comprehensive analysis
- Performance is mixed (53% accuracy) to generate meaningful diagnostics

