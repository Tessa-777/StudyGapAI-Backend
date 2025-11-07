# Decisions Summary - AI/SE Full Integration

## Purpose
This document summarizes all decisions needed before proceeding with the AI/SE full integration implementation. Please review and provide decisions for each item.

---

## 1. API Input Format

### Decision Required: How should the frontend send quiz data?

**Option A**: Frontend sends complete quiz data in new format
```json
{
  "subject": "Mathematics",
  "total_questions": 30,
  "time_taken": 15.5,
  "questions_list": [...]
}
```

**Option B**: Frontend sends quiz_id, backend fetches and transforms
```json
{
  "quiz_id": "uuid-here"
}
```

**Option C**: Hybrid - Support both formats

**Recommendation**: Option A (cleaner, more explicit)

**Your Decision**: Option A

---

## 2. Confidence Scores

### Decision Required: How should confidence scores be handled?

**Current Situation**: Existing quiz responses may not have confidence scores

**Option A**: Make confidence required (1-5 scale), frontend must provide
- Pros: More accurate analysis
- Cons: Frontend must collect this data

**Option B**: Make confidence optional, default to 3 if not provided
- Pros: Works with existing data
- Cons: Less accurate analysis

**Option C**: Infer confidence from other factors (time spent, explanation quality)
- Pros: Smart default
- Cons: May be inaccurate

**Recommendation**: Option A (require confidence for new implementation)

**Your Decision**: Option C

---

## 3. Topic Information

### Decision Required: How should topic information be provided?

**Current Situation**: Questions may have topic_id, but we need topic name for AI analysis

**Option A**: Frontend provides topic name in each question response
- Pros: Simple, explicit
- Cons: Frontend must know topics

**Option B**: Backend looks up topic from question_id
- Pros: Single source of truth
- Cons: Requires database lookup

**Option C**: Questions table has both topic_id and topic name
- Pros: Best of both worlds
- Cons: Data duplication

**Recommendation**: Option C (store topic name in questions table for performance)

**Your Decision**: Option C

---

## 4. Study Plan Endpoint

### Decision Required: Should study plan have a separate endpoint?

**Context**: Study plan is included in diagnostic analysis response

**Option A**: Remove separate endpoint, study plan always comes with diagnostic
- Pros: Simpler, consistent
- Cons: Cannot regenerate study plan without re-running analysis

**Option B**: Keep separate endpoint that extracts study plan from diagnostic
- Pros: Allows accessing study plan separately
- Cons: Redundant data

**Option C**: Keep separate endpoint that can regenerate study plan
- Pros: Most flexible
- Cons: More complex, may need to re-run AI

**Recommendation**: Option B (keep endpoint for convenience, but it just extracts from diagnostic)

**Your Decision**: Option A

---

## 5. Time Tracking

### Decision Required: How should time_taken be calculated?

**Option A**: Frontend provides total time_taken in minutes
- Pros: Accurate, frontend knows actual time
- Cons: Frontend must track time

**Option B**: Backend calculates from sum of time_spent_seconds in responses
- Pros: Automatic
- Cons: May not account for breaks

**Option C**: Both - Frontend provides, backend validates against response times
- Pros: Most accurate
- Cons: More complex

**Recommendation**: Option A (frontend provides, simpler)

**Your Decision**: Option A

---

## 6. Error Type Classification

### Decision Required: Should we validate error types?

**Context**: Documentation defines 5 error types:
- conceptual_gap
- procedural_error
- careless_mistake
- knowledge_gap
- misinterpretation

**Option A**: Strict validation - Only accept these 5 types
- Pros: Data consistency
- Cons: May reject valid variations

**Option B**: Flexible - Allow any string, but prefer these 5
- Pros: More flexible
- Cons: Less consistent

**Recommendation**: Option A (strict validation for data quality)

**Your Decision**: Option A

---

## 7. Fluency Index Calculation

### Decision Required: Should we validate Fluency Index calculations?

**Context**: Documentation specifies: `FI = (Topic Accuracy) * (Average Topic Confidence / 5)`

**Option A**: Trust AI to calculate correctly, just validate format
- Pros: Simpler
- Cons: May have calculation errors

**Option B**: Backend recalculates and validates AI's calculations
- Pros: Ensures accuracy
- Cons: More complex, may need to correct AI

**Recommendation**: Option B (validate calculations for data integrity)

**Your Decision**: Option B

---

## 8. JAMB Score Projection

### Decision Required: Should we validate JAMB score calculations?

**Context**: Documentation specifies: `Base Score = (Quiz Accuracy) * 400`, `Final Score = min(max(Base + Adjustment + Bonus, 0), 400)`

**Option A**: Trust AI to calculate correctly
- Pros: Simpler
- Cons: May have calculation errors

**Option B**: Backend recalculates base score, validate it's in 0-400 range
- Pros: Ensures score is valid
- Cons: AI's adjustments/bonuses may be lost

**Recommendation**: Option A (trust AI, but validate score is 0-400)

**Your Decision**: Option B

---

## 9. Study Plan Duration

### Decision Required: Should study plan always be 6 weeks?

**Context**: Documentation shows 6-week study plans

**Option A**: Always 6 weeks (fixed)
- Pros: Consistent with documentation
- Cons: Not flexible

**Option B**: Configurable (4, 6, 8, 12 weeks)
- Pros: More flexible
- Cons: Need to update prompts

**Option C**: AI decides based on performance
- Pros: Most adaptive
- Cons: Inconsistent, harder to validate

**Recommendation**: Option A (start with 6 weeks, can add flexibility later)

**Your Decision**: Option A

---

## 10. Database Storage Strategy

### Decision Required: How should we store the analysis result?

**Option A**: Store only analysis_result (single JSONB column)
- Pros: Simple, preserves exact AI output
- Cons: Harder to query specific fields

**Option B**: Store analysis_result + denormalized fields (recommended in plan)
- Pros: Easy querying, preserves original
- Cons: Data duplication

**Option C**: Store only denormalized fields, no original
- Pros: Easy querying
- Cons: Lose original AI output

**Recommendation**: Option B (store both for flexibility)

**Your Decision**: Option B

---

## 11. Authentication & Authorization

### Decision Required: Should authentication be required for all endpoints?

**Option A**: All endpoints require authentication (current approach)
- Pros: Secure, consistent
- Cons: Cannot test without auth

**Option B**: Diagnostic analysis requires auth, explain-answer is public
- Pros: Flexible
- Cons: Mixed approach

**Recommendation**: Option A (keep current approach, all endpoints require auth)

**Your Decision**: Option A

---

## 12. Mock Mode

### Decision Required: Should mock mode return realistic data?

**Option A**: Return realistic mock data matching new format
- Pros: Good for testing frontend
- Cons: May not catch format issues

**Option B**: Return simplified mock data
- Pros: Faster development
- Cons: Less realistic

**Recommendation**: Option A (realistic mock data for better testing)

**Your Decision**: Option A

---

## 13. Caching Strategy

### Decision Required: How should we cache AI responses?

**Option A**: Cache by exact input (current approach)
- Pros: Prevents duplicate API calls
- Cons: Same quiz analyzed twice gets cached result

**Option B**: No caching (always call AI)
- Pros: Always fresh results
- Cons: Expensive, slow

**Option C**: Cache by quiz_id (one analysis per quiz)
- Pros: One analysis per quiz
- Cons: Cannot re-analyze

**Recommendation**: Option A (keep current caching approach)

**Your Decision**: Option A

---

## 14. Error Handling

### Decision Required: How should we handle AI API errors?

**Option A**: Return error to frontend, let them retry
- Pros: Simple
- Cons: User sees errors

**Option B**: Automatic retry with exponential backoff
- Pros: Better UX
- Cons: May delay response

**Option C**: Queue for background processing
- Pros: Non-blocking
- Cons: Complex, need queue system

**Recommendation**: Option A (start simple, add retries later if needed)

**Your Decision**: Option A

---

## 15. Response Validation

### Decision Required: How strict should response validation be?

**Option A**: Strict - Reject if any field doesn't match schema
- Pros: Data quality
- Cons: May reject valid but slightly different responses

**Option B**: Lenient - Accept if core fields present, ignore extras
- Pros: More flexible
- Cons: May accept invalid data

**Option C**: Strict validation with helpful error messages
- Pros: Best of both worlds
- Cons: More complex error handling

**Recommendation**: Option C (strict validation with good error messages)

**Your Decision**: Option C

---

## Summary of Recommendations

| Decision | Recommendation | Rationale |
|----------|---------------|-----------|
| 1. API Input Format | Option A | Cleaner, more explicit |
| 2. Confidence Scores | Option A | Required for accurate analysis |
| 3. Topic Information | Option C | Store topic name in questions table |
| 4. Study Plan Endpoint | Option B | Keep for convenience, extract from diagnostic |
| 5. Time Tracking | Option A | Frontend provides time |
| 6. Error Type Classification | Option A | Strict validation for consistency |
| 7. Fluency Index | Option B | Validate calculations |
| 8. JAMB Score | Option A | Trust AI, validate range |
| 9. Study Plan Duration | Option A | Fixed 6 weeks |
| 10. Database Storage | Option B | Store both original and denormalized |
| 11. Authentication | Option A | All endpoints require auth |
| 12. Mock Mode | Option A | Realistic mock data |
| 13. Caching | Option A | Cache by input hash |
| 14. Error Handling | Option A | Return errors, no retry (yet) |
| 15. Response Validation | Option C | Strict with good error messages |

---

## Action Items

1. Review all decisions above
2. Provide your decision for each item (or approve recommendations)
3. Clarify any questions or concerns
4. Approve plan to proceed with implementation

---

**Document Version**: 1.0  
**Created**: 2025-01-27  
**Status**: Awaiting Decisions

