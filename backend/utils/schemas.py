from typing import List, Optional
from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
	email: str
	name: str
	phone: Optional[str] = None


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


class AnalyzeDiagnosticRequest(BaseModel):
	userId: Optional[str] = None  # Optional - will use JWT if not provided
	quizId: str
	responses: List[SubmitResponse]


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


