from flask import Blueprint, current_app, jsonify, request

from ..utils.validation import require_fields
from ..utils.validate import validate_json
from ..utils.schemas import StartQuizRequest, SubmitQuizRequest
from ..utils.auth import require_auth, get_current_user_id


quiz_bp = Blueprint("quiz", __name__)


def _repo():
	"""Get the repository instance from app context"""
	return current_app.extensions.get("repository")


def _cache():
	"""Get cache instance safely"""
	try:
		return current_app.extensions.get("cache_instance")
	except (RuntimeError, AttributeError):
		return None


@quiz_bp.get("/questions")
def get_questions():
	"""Public endpoint - no auth required for questions"""
	cache = _cache()
	key = f"questions:{int(request.args.get('total', 30))}"
	if cache:
		cached = cache.get(key)
		if cached:
			return jsonify(cached), 200
	questions = _repo().get_diagnostic_questions(total=int(request.args.get("total", 30)))
	if cache:
		cache.set(key, questions, timeout=120)
	return jsonify(questions), 200


@quiz_bp.post("/quiz/start")
@require_auth
@validate_json(StartQuizRequest)
def start_quiz(current_user_id):
	"""Start a new quiz - requires authentication"""
	data = request.get_json(force=True) or {}
	# Use authenticated user_id from JWT, not from request body
	quiz = _repo().create_quiz({
		"user_id": current_user_id,
		"total_questions": int(data.get("totalQuestions", 30))
	})
	return jsonify(quiz), 201


@quiz_bp.post("/quiz/<quiz_id>/submit")
@require_auth
@validate_json(SubmitQuizRequest)
def submit_quiz(quiz_id: str, current_user_id):
	"""Submit quiz responses - requires authentication and validates ownership"""
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["responses"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	repo = _repo()
	try:
		# Verify quiz belongs to current user
		quiz = repo.get_quiz_results(quiz_id)
		if not quiz or quiz.get("quiz", {}).get("user_id") != current_user_id:
			return jsonify({"error": "forbidden", "message": "Quiz not found or access denied"}), 403
		
		responses = []
		for r in data["responses"]:
			responses.append({
				"quiz_id": quiz_id,
				"question_id": r.get("questionId"),
				"student_answer": r.get("studentAnswer"),
				"correct_answer": r.get("correctAnswer"),
				"is_correct": bool(r.get("isCorrect")),
				"explanation_text": r.get("explanationText"),
				"time_spent_seconds": int(r.get("timeSpentSeconds", 0)),
			})
		repo.save_quiz_responses(quiz_id, responses)
		return jsonify({"status": "submitted"}), 200
	except KeyError:
		return jsonify({"error": "not_found", "message": "Quiz not found"}), 404
	except Exception as e:
		return jsonify({"error": "server_error", "message": str(e)}), 500


@quiz_bp.get("/quiz/<quiz_id>/results")
@require_auth
def quiz_results(quiz_id: str, current_user_id):
	"""Get quiz results - requires authentication and validates ownership"""
	repo = _repo()
	cache = _cache()
	key = f"quiz_results:{quiz_id}"
	if cache:
		cached = cache.get(key)
		if cached:
			# Verify ownership even for cached results
			if cached.get("quiz", {}).get("user_id") != current_user_id:
				return jsonify({"error": "forbidden", "message": "Access denied"}), 403
			return jsonify(cached), 200
	try:
		results = repo.get_quiz_results(quiz_id)
		# Verify ownership
		if not results or results.get("quiz", {}).get("user_id") != current_user_id:
			return jsonify({"error": "forbidden", "message": "Quiz not found or access denied"}), 403
		if cache:
			cache.set(key, results, timeout=120)
		return jsonify(results), 200
	except KeyError:
		return jsonify({"error": "not_found", "message": "Quiz not found"}), 404
	except Exception as e:
		return jsonify({"error": "server_error", "message": str(e)}), 500


