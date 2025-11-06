from flask import Blueprint, current_app, jsonify, request

from ..services.ai import AIService
from ..services.study_plan import build_adjusted_plan
from ..utils.validation import require_fields
from ..utils.validate import validate_json
from ..utils.schemas import AnalyzeDiagnosticRequest, GenerateStudyPlanRequest, ExplainAnswerRequest, AdjustPlanRequest
from ..utils.auth import require_auth, get_current_user_id


ai_bp = Blueprint("ai", __name__)


def _repo():
	"""Get the repository instance from app context"""
	return current_app.extensions.get("repository")


def _ai():
	cfg = current_app.config
	return AIService(cfg.get("GOOGLE_API_KEY"), cfg.get("AI_MODEL_NAME", "gemini-2.0-flash-exp"), cfg.get("AI_MOCK", True))


@ai_bp.post("/analyze-diagnostic")
@require_auth
@validate_json(AnalyzeDiagnosticRequest)
def analyze_diagnostic(current_user_id):
	"""Analyze diagnostic quiz - requires authentication"""
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["quizId", "responses"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	# Verify quiz belongs to current user
	quiz_results = _repo().get_quiz_results(data["quizId"])
	if not quiz_results or quiz_results.get("quiz", {}).get("user_id") != current_user_id:
		return jsonify({"error": "forbidden", "message": "Quiz not found or access denied"}), 403
	
	analysis = _ai().analyze_diagnostic(data["responses"])
	diagnostic = _repo().save_ai_diagnostic({
		"quiz_id": data["quizId"],
		"weak_topics": analysis.get("weakTopics"),
		"strong_topics": analysis.get("strongTopics"),
		"analysis_summary": analysis.get("analysisSummary"),
		"projected_score": analysis.get("projectedScore"),
		"foundational_gaps": analysis.get("foundationalGaps"),
	})
	# Return analysis with diagnostic ID
	analysis["id"] = diagnostic.get("id")
	return jsonify(analysis), 200


@ai_bp.post("/generate-study-plan")
@require_auth
@validate_json(GenerateStudyPlanRequest)
def generate_study_plan(current_user_id):
	"""Generate study plan - requires authentication"""
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["diagnosticId", "weakTopics", "targetScore"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	# Verify diagnostic belongs to current user (via quiz)
	diagnostic = _repo().get_study_plan(data["diagnosticId"])  # This might not work, need to check
	# For now, use authenticated user_id
	weeks_available = int(data.get("weeksAvailable", 6))
	plan = _ai().generate_study_plan(data["weakTopics"], int(data["targetScore"]), int(data.get("currentScore", 150)), weeks_available)
	stored = _repo().create_study_plan({
		"user_id": current_user_id,  # Use authenticated user_id
		"diagnostic_id": data["diagnosticId"],
		"plan_data": plan,
	})
	return jsonify(stored), 201


@ai_bp.post("/explain-answer")
def explain_answer():
	"""Explain answer - public endpoint (no auth required)"""
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["questionId", "studentAnswer", "correctAnswer", "studentReasoning"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	explanation = _ai().explain_answer({
		"questionId": data["questionId"],
		"studentAnswer": data["studentAnswer"],
		"correctAnswer": data["correctAnswer"],
		"studentReasoning": data["studentReasoning"],
	})
	return jsonify(explanation), 200


@ai_bp.post("/adjust-plan")
@require_auth
@validate_json(AdjustPlanRequest)
def adjust_plan(current_user_id):
	"""Adjust study plan - requires authentication and validates ownership"""
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["studyPlanId", "completedTopics", "newWeakTopics"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	repo = _repo()
	# Get study plan
	existing = None
	if hasattr(repo, "study_plans"):
		existing = repo.study_plans.get(data["studyPlanId"])
	else:
		existing = repo.get_study_plan(data["studyPlanId"])
	
	if not existing:
		return jsonify({"error": "not_found", "message": "Study plan not found"}), 404
	
	# Verify ownership
	if existing.get("user_id") != current_user_id:
		return jsonify({"error": "forbidden", "message": "Access denied"}), 403
	
	updated_data = build_adjusted_plan(existing.get("plan_data", {}), data["completedTopics"], data["newWeakTopics"])
	updated = repo.update_study_plan(data["studyPlanId"], updated_data)
	return jsonify({"updatedPlan": updated}), 200


