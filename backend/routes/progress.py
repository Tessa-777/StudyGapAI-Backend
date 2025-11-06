from flask import Blueprint, current_app, jsonify, request

from ..utils.validation import require_fields
from ..utils.validate import validate_json
from ..utils.schemas import AdjustPlanRequest
from ..utils.auth import require_auth, get_current_user_id


progress_bp = Blueprint("progress", __name__)


def _repo():
	"""Get the repository instance from app context"""
	return current_app.extensions.get("repository")


@progress_bp.get("/users/<user_id>/progress")
@require_auth
def get_progress(user_id: str, current_user_id):
	"""Get user progress - requires authentication and validates ownership"""
	# Verify user can only access their own progress
	if user_id != current_user_id:
		return jsonify({"error": "forbidden", "message": "Cannot access other users' progress"}), 403
	
	items = _repo().get_user_progress(user_id)
	return jsonify(items), 200


# New endpoint: Get current user's progress
@progress_bp.get("/progress")
@require_auth
def get_current_progress(current_user_id):
	"""Get current authenticated user's progress"""
	items = _repo().get_user_progress(current_user_id)
	return jsonify(items), 200


@progress_bp.post("/progress/mark-complete")
@require_auth
def mark_complete(current_user_id):
	"""Mark progress complete - requires authentication"""
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["topicId", "status"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	# Use authenticated user_id, not from request body
	entry = _repo().mark_progress_complete({
		"user_id": current_user_id,
		"topic_id": data["topicId"],
		"status": data.get("status", "completed"),
		"resources_viewed": int(data.get("resourcesViewed", 0)),
		"practice_problems_completed": int(data.get("practiceProblemsCompleted", 0)),
	})
	return jsonify(entry), 201


