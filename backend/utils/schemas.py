from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class RegisterRequest(BaseModel):
	email: str
	name: str
	phone: Optional[str] = None
	targetScore: Optional[int] = Field(default=None, ge=0, le=400, description="Target JAMB score (0-400)")


class LoginRequest(BaseModel):
	email: str
	name: Optional[str] = None


class UpdateTargetScoreRequest(BaseModel):
	targetScore: int = Field(ge=0)


class StartQuizRequest(BaseModel):
	userId: Optional[str] = None  # Optional - will use JWT if not provided
	totalQuestions: Optional[int] = 30


class SubmitResponse(BaseModel):
	questionId: str
	studentAnswer: str
	correctAnswer: str
	isCorrect: bool
	explanationText: Optional[str] = ""
	timeSpentSeconds: Optional[int] = 0


class SubmitQuizRequest(BaseModel):
	responses: List[SubmitResponse]


# New AI/SE Schema - Decision 1: Option A - Frontend sends complete quiz data
class QuestionResponse(BaseModel):
	"""Question response for AI/SE diagnostic analysis"""
	id: int = Field(description="Question ID or index")
	topic: str = Field(description="Topic name (e.g., 'Algebra', 'Geometry')")
	student_answer: str = Field(description="Student's answer (A, B, C, or D)")
	correct_answer: str = Field(description="Correct answer (A, B, C, or D)")
	is_correct: bool = Field(description="Whether the answer is correct")
	confidence: Optional[int] = Field(default=None, ge=1, le=5, description="Confidence score 1-5 (will be inferred if not provided)")
	explanation: str = Field(default="", description="Student's explanation for their answer")
	time_spent_seconds: Optional[int] = Field(default=None, ge=0, description="Time spent on question in seconds")
	
	@field_validator('student_answer', 'correct_answer')
	@classmethod
	def validate_answer(cls, v: str) -> str:
		if v.upper() not in ['A', 'B', 'C', 'D']:
			raise ValueError('Answer must be A, B, C, or D')
		return v.upper()


class AnalyzeDiagnosticRequest(BaseModel):
	"""Request for AI/SE diagnostic analysis - Decision 1: Option A"""
	subject: str = Field(description="Subject name (e.g., 'Mathematics', 'Physics')")
	total_questions: int = Field(gt=0, description="Total number of questions")
	time_taken: float = Field(gt=0, description="Total time taken in minutes - Decision 5: Option A")
	questions_list: List[QuestionResponse] = Field(min_length=1, description="List of question responses")
	quiz_id: Optional[str] = Field(default=None, description="Optional quiz ID if linking to existing quiz")


# Response schemas for AI diagnostic analysis
class OverallPerformance(BaseModel):
	accuracy: float = Field(ge=0, le=100)
	total_questions: int = Field(gt=0)
	correct_answers: int = Field(ge=0)
	avg_confidence: float = Field(ge=1, le=5)
	time_per_question: float = Field(ge=0)


class TopicBreakdown(BaseModel):
	topic: str
	accuracy: float = Field(ge=0, le=100)
	fluency_index: float = Field(ge=0, le=100)
	status: str = Field(pattern="^(weak|developing|strong)$")
	questions_attempted: int = Field(gt=0)
	severity: Optional[str] = Field(default=None, pattern="^(critical|moderate|mild)$")
	dominant_error_type: Optional[str] = Field(default=None)


class RootCauseAnalysis(BaseModel):
	primary_weakness: str = Field(pattern="^(conceptual_gap|procedural_error|careless_mistake|knowledge_gap|misinterpretation)$")
	error_distribution: Dict[str, int] = Field(description="Distribution of error types")


class PredictedJambScore(BaseModel):
	score: int = Field(ge=0, le=400)
	confidence_interval: str


class WeeklySchedule(BaseModel):
	week: int = Field(ge=1, le=6)
	focus: str
	study_hours: int = Field(ge=0)
	key_activities: List[str] = Field(min_length=1)


class StudyPlan(BaseModel):
	weekly_schedule: List[WeeklySchedule] = Field(min_length=1, max_length=6)


class Recommendation(BaseModel):
	priority: int = Field(ge=1)
	category: str
	action: str
	rationale: str


class AnalyzeDiagnosticResponse(BaseModel):
	"""Complete AI/SE diagnostic analysis response"""
	id: str
	overall_performance: OverallPerformance
	topic_breakdown: List[TopicBreakdown]
	root_cause_analysis: RootCauseAnalysis
	predicted_jamb_score: PredictedJambScore
	study_plan: StudyPlan
	recommendations: List[Recommendation]
	analysis_summary: str = Field(description="Text summary of the diagnostic analysis from Gemini")
	generated_at: str


# Legacy schemas (kept for backward compatibility if needed)
class GenerateStudyPlanRequest(BaseModel):
	userId: Optional[str] = None  # Optional - will use JWT if not provided
	diagnosticId: str
	weakTopics: list
	targetScore: int
	weeksAvailable: Optional[int] = 6
	currentScore: Optional[int] = 150


class ExplainAnswerRequest(BaseModel):
	questionId: str
	studentAnswer: str
	correctAnswer: str
	studentReasoning: str


class AdjustPlanRequest(BaseModel):
	userId: Optional[str] = None  # Optional - will use JWT if not provided
	studyPlanId: str
	completedTopics: List[str]
	newWeakTopics: List[str]


class SaveDiagnosticRequest(BaseModel):
	"""Request to save a guest diagnostic after user signs up"""
	# Quiz data (original submission)
	subject: str = Field(description="Subject name (e.g., 'Mathematics')")
	total_questions: int = Field(gt=0, description="Total number of questions")
	time_taken: float = Field(gt=0, description="Total time taken in minutes")
	questions_list: List[QuestionResponse] = Field(min_length=1, description="List of question responses")
	
	# Diagnostic data (from the guest diagnostic response)
	# Optional - if not provided, will be regenerated from quiz data
	# Using Dict[str, Any] instead of AnalyzeDiagnosticResponse to be more flexible
	# The diagnostic might have additional fields or slightly different structure
	diagnostic: Optional[Dict[str, Any]] = Field(default=None, description="Complete diagnostic result from guest submission (optional - will be regenerated if not provided)")


