from flask import Blueprint, current_app, jsonify, request

from ..utils.validation import require_fields
from ..utils.validate import validate_json
from ..utils.schemas import RegisterRequest, LoginRequest, UpdateTargetScoreRequest
from ..utils.auth import require_auth, get_current_user_id, optional_auth


users_bp = Blueprint("users", __name__)


def _repo():
	"""Get the repository instance from app context"""
	return current_app.extensions.get("repository")


@users_bp.post("/register")
@validate_json(RegisterRequest)
def register():
	"""
	User registration endpoint
	Note: With Supabase Auth, registration happens on frontend via Auth SDK
	This endpoint can sync user data to our users table after Auth registration
	"""
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["email", "name"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	# Get user_id from JWT if authenticated, otherwise from request
	user_id = get_current_user_id() or data.get("userId")
	
	if user_id:
		# User is authenticated - sync to users table
		user = _repo().upsert_user({
			"id": user_id,
			"email": data["email"],
			"name": data["name"],
			"phone": data.get("phone")
		})
	else:
		# Fallback: create user without auth (for backward compatibility)
		user = _repo().upsert_user({
			"email": data["email"],
			"name": data["name"],
			"phone": data.get("phone")
		})
	return jsonify(user), 201


@users_bp.post("/login")
@optional_auth
def login(current_user_id=None):
	"""
	Login endpoint
	Note: With Supabase Auth, login happens on frontend via Auth SDK
	This endpoint returns user info if authenticated, or allows email-based lookup
	"""
	if current_user_id:
		# User is authenticated via JWT - return their info
		user = _repo().get_user(current_user_id)
		if user:
			return jsonify({"user": user, "authenticated": True}), 200
	
	# Fallback: email-based lookup (for backward compatibility)
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["email"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	user = _repo().get_user_by_email(data["email"]) or _repo().upsert_user({
		"email": data["email"],
		"name": data.get("name", "Student")
	})
	return jsonify({"user": user, "authenticated": False, "message": "Use Supabase Auth for full authentication"}), 200


@users_bp.get("/me")
@require_auth
def get_current_user(current_user_id):
	"""Get current authenticated user's profile"""
	user = _repo().get_user(current_user_id)
	if not user:
		return jsonify({"error": "not_found"}), 404
	return jsonify(user), 200


@users_bp.get("/<user_id>")
@optional_auth
def get_user(user_id: str, current_user_id=None):
	"""Get user by ID - requires auth if accessing other users"""
	# Allow users to read their own profile, or if no auth provided (backward compat)
	if current_user_id and user_id != current_user_id:
		return jsonify({"error": "forbidden", "message": "Cannot access other users' profiles"}), 403
	
	user = _repo().get_user(user_id)
	if not user:
		return jsonify({"error": "not_found"}), 404
	return jsonify(user), 200


@users_bp.put("/target-score")
@require_auth
def update_target(current_user_id):
	"""Update current user's target score"""
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["targetScore"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	repo = _repo()
	try:
		user = repo.update_user_target_score(current_user_id, int(data["targetScore"]))
		return jsonify(user), 200
	except KeyError:
		return jsonify({"error": "not_found", "message": "User not found"}), 404
	except Exception as e:
		return jsonify({"error": "server_error", "message": str(e)}), 500


# Legacy endpoint for backward compatibility
@users_bp.put("/<user_id>/target-score")
@optional_auth
def update_target_legacy(user_id: str, current_user_id=None):
	"""Legacy endpoint - use /target-score instead"""
	# Validate ownership if authenticated
	if current_user_id and user_id != current_user_id:
		return jsonify({"error": "forbidden", "message": "Cannot update other users' target score"}), 403
	
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["targetScore"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	repo = _repo()
	try:
		user = repo.update_user_target_score(user_id, int(data["targetScore"]))
		return jsonify(user), 200
	except KeyError:
		return jsonify({"error": "not_found", "message": "User not found"}), 404
	except Exception as e:
		return jsonify({"error": "server_error", "message": str(e)}), 500


