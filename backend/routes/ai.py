from flask import Blueprint, current_app, jsonify, request
from datetime import datetime, timezone
import uuid

from ..services.ai_enhanced import EnhancedAIService, AIAPIError
from ..services.confidence_inference import add_confidence_scores
from ..services.study_plan import build_adjusted_plan
from ..utils.validation import require_fields
from ..utils.validate import validate_json
from ..utils.schemas import (
	AnalyzeDiagnosticRequest, 
	GenerateStudyPlanRequest, 
	ExplainAnswerRequest, 
	AdjustPlanRequest,
	AnalyzeDiagnosticResponse,
	SaveDiagnosticRequest
)
from ..utils.auth import require_auth, optional_auth, get_current_user_id, get_auth


ai_bp = Blueprint("ai", __name__)


def _repo():
	"""Get the repository instance from app context"""
	return current_app.extensions.get("repository")


def _ai():
	"""Get the enhanced AI service instance"""
	cfg = current_app.config
	# Handle AI_MOCK as both string and boolean
	ai_mock = cfg.get("AI_MOCK", "true")
	if isinstance(ai_mock, bool):
		mock_mode = ai_mock
	else:
		mock_mode = str(ai_mock).lower() == "true"
	
	api_key = cfg.get("GOOGLE_API_KEY")
	model_name = cfg.get("AI_MODEL_NAME", "gemini-1.5-flash")
	
	# Log AI service initialization for debugging
	current_app.logger.info(f"Initializing AI Service: mock={mock_mode}, has_api_key={bool(api_key)}, model={model_name}")
	
	ai_service = EnhancedAIService(api_key, model_name, mock_mode)
	
	# Log final mock mode (EnhancedAIService might override it if API key is missing)
	current_app.logger.info(f"AI Service initialized: mock={ai_service.mock}, model={ai_service.model_name}")
	
	return ai_service


@ai_bp.post("/analyze-diagnostic")
@optional_auth  # Changed from @require_auth to allow guest users
@validate_json(AnalyzeDiagnosticRequest)
def analyze_diagnostic(current_user_id=None):
	"""
	Analyze diagnostic quiz - Enhanced AI/SE implementation
	Decision 1: Option A - Frontend sends complete quiz data
	Decision 4: Option A - Study plan included in diagnostic (no separate endpoint)
	
	Supports both authenticated and guest users:
	- Authenticated users: Diagnostic saved to database
	- Guest users: Diagnostic generated but not saved (frontend stores in localStorage)
	"""
	data = request.get_json(force=True) or {}
	
	# Determine if user is authenticated (guest mode)
	is_guest = current_user_id is None
	
	# Log authentication status and request details
	auth_header = request.headers.get("Authorization", "")
	has_auth_header = bool(auth_header)
	current_app.logger.info(f"📋 Quiz submission received: is_guest={is_guest}, has_auth_header={has_auth_header}, current_user_id={current_user_id}")
	
	if is_guest:
		current_app.logger.info("👤 Guest user submitting quiz (no authentication)")
		if has_auth_header:
			current_app.logger.warning("⚠️ Guest user but Authorization header present - token might be invalid or expired")
	else:
		current_app.logger.info(f"👤 Authenticated user submitting quiz: {current_user_id}")
		if not has_auth_header:
			current_app.logger.warning("⚠️ Authenticated user but no Authorization header - this shouldn't happen")
	
	# Validate required fields
	ok, missing = require_fields(data, ["subject", "total_questions", "time_taken", "questions_list"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	# Optional: Verify quiz belongs to current user if quiz_id provided AND user is authenticated
	quiz_id = data.get("quiz_id")
	if quiz_id and current_user_id:
		try:
			quiz_results = _repo().get_quiz_results(quiz_id)
			if not quiz_results or quiz_results.get("quiz", {}).get("user_id") != current_user_id:
				return jsonify({"error": "forbidden", "message": "Quiz not found or access denied"}), 403
		except KeyError:
			# Quiz doesn't exist, that's okay - we'll create one if needed
			pass
	elif quiz_id and is_guest:
		# Guest users shouldn't provide quiz_id (they don't have quizzes yet)
		current_app.logger.warning("Guest user provided quiz_id - ignoring it")
		quiz_id = None
	
	# Prepare quiz data for AI service
	questions_list = [
		{
			"id": q.get("id", idx + 1),
			"topic": q.get("topic"),
			"student_answer": q.get("student_answer"),
			"correct_answer": q.get("correct_answer"),
			"is_correct": q.get("is_correct"),
			"confidence": q.get("confidence"),  # Will be inferred if not provided
			"explanation": q.get("explanation", ""),
			"time_spent_seconds": q.get("time_spent_seconds"),
		}
		for idx, q in enumerate(data["questions_list"])
	]
	
	# Add confidence scores if not provided (Decision 2: Option C)
	questions_with_confidence = add_confidence_scores(questions_list)
	
	quiz_data = {
		"subject": data["subject"],
		"total_questions": data["total_questions"],
		"time_taken": data["time_taken"],
		"questions_list": questions_with_confidence
	}
	
	# Call enhanced AI service
	try:
		ai_service = _ai()
		
		# Log whether we're using mock or real AI
		if ai_service.mock:
			current_app.logger.warning("⚠️⚠️⚠️ USING MOCK AI MODE - No real AI calls will be made! ⚠️⚠️⚠️")
		else:
			current_app.logger.info("✅✅✅ Using REAL AI mode - Gemini API will be called ✅✅✅")
		
		current_app.logger.info(f"Calling AI service with {len(questions_with_confidence)} questions for analysis")
		analysis = ai_service.analyze_diagnostic(quiz_data)
		
		# Log if analysis was generated
		if ai_service.mock:
			current_app.logger.info("📊 Mock analysis generated (no API call made)")
		else:
			current_app.logger.info("🤖✅ Real AI analysis generated from Gemini API - Check your API usage!")
			
	except AIAPIError as e:
		current_app.logger.error(f"AI API error: {e.message} (Status: {e.status_code})", exc_info=True)
		# Return user-friendly error message
		error_response = {
			"error": "ai_service_error",
			"message": e.message,
			"status_code": e.status_code
		}
		# Add retry suggestion for timeout/abort errors
		if e.status_code == 408:
			error_response["retryable"] = True
			error_response["suggestion"] = "The request was interrupted. Please try again in a moment."
		return jsonify(error_response), e.status_code
	except ValueError as e:
		current_app.logger.error(f"Validation error: {str(e)}", exc_info=True)
		return jsonify({"error": "validation_error", "message": str(e)}), 400
	except Exception as e:
		current_app.logger.error(f"Error in analyze_diagnostic: {str(e)}", exc_info=True)
		return jsonify({"error": "internal_error", "message": "An unexpected error occurred while analyzing diagnostic"}), 500
	
	# Handle authenticated users: Ensure user exists and create quiz
	# For guest users: Skip database operations (diagnostic not saved)
	if current_user_id:
		# Authenticated user: Ensure user exists in users table (auto-create if needed)
		try:
			user = _repo().get_user(current_user_id)
			if not user:
				# User doesn't exist, create them
				# Try to get email and name from JWT token payload
				email = f"user_{current_user_id[:8]}@example.com"  # Default placeholder
				name = "Student"  # Default name
				
				# Extract user info from JWT token if available
				try:
					auth_header = request.headers.get("Authorization", "")
					if auth_header:
						auth = get_auth()
						if auth:
							user_info = auth.verify_token(auth_header)
							if user_info:
								# Get email from token
								token_email = user_info.get("email")
								if token_email:
									email = token_email
								
								# Try to get name from user metadata
								payload = user_info.get("payload", {})
								if payload:
									user_metadata = payload.get("user_metadata", {})
									if user_metadata and user_metadata.get("name"):
										name = user_metadata.get("name")
									elif payload.get("name"):
										name = payload.get("name")
				except Exception as e:
					current_app.logger.debug(f"Could not extract user info from JWT: {str(e)}")
				
				# Create user in users table
				user = _repo().upsert_user({
					"id": current_user_id,
					"email": email,
					"name": name
				})
				current_app.logger.info(f"Auto-created user in users table: {current_user_id} ({email})")
		except Exception as e:
			current_app.logger.error(f"Error ensuring user exists: {str(e)}", exc_info=True)
			# Continue anyway - the quiz creation will fail with a clearer error if user still doesn't exist
		
		# Create quiz if quiz_id not provided, or verify quiz exists if provided
		if not quiz_id:
			# Create new quiz for authenticated user
			try:
				current_app.logger.info(f"Creating quiz for user {current_user_id}: subject={data.get('subject')}, total_questions={data.get('total_questions')}, time_taken={data.get('time_taken')}")
				quiz = _repo().create_quiz({
					"user_id": current_user_id,
					"subject": data["subject"],
					"total_questions": data["total_questions"],
					"time_taken_minutes": data["time_taken"],
					"completed_at": datetime.now(timezone.utc).isoformat(),
				})
				quiz_id = quiz.get("id")
				if not quiz_id:
					current_app.logger.error(f"❌ Quiz created but no ID returned. Quiz data: {quiz}")
					return jsonify({"error": "internal_error", "message": "Failed to create quiz - no ID returned"}), 500
				current_app.logger.info(f"✅ Created quiz for authenticated user: {quiz_id} (user_id: {current_user_id})")
			except Exception as e:
				current_app.logger.error(f"❌ Error creating quiz for user {current_user_id}: {str(e)}", exc_info=True)
				# Check if it's a foreign key error for user_id
				error_str = str(e).lower()
				if "user_id" in error_str and ("not present in table" in error_str or "foreign key" in error_str):
					current_app.logger.error(f"❌ User {current_user_id} does not exist in database")
					return jsonify({
						"error": "user_not_found", 
						"message": "User does not exist in database. Please ensure user is registered in the users table."
					}), 400
				return jsonify({"error": "internal_error", "message": f"Failed to create quiz: {str(e)}"}), 500
		
		# Save quiz responses for authenticated users
		try:
			responses = [
				{
					"question_id": None,  # question_id is optional - can be None if question doesn't exist in DB yet
					"topic": q.get("topic"),
					"student_answer": q.get("student_answer"),
					"correct_answer": q.get("correct_answer"),
					"is_correct": q.get("is_correct"),
					"confidence": q.get("confidence", 3),  # Confidence was inferred above
					"explanation": q.get("explanation", ""),
					"time_spent_seconds": q.get("time_spent_seconds"),
				}
				for idx, q in enumerate(questions_with_confidence)
			]
			current_app.logger.info(f"Saving {len(responses)} quiz responses for quiz {quiz_id}")
			_repo().save_quiz_responses(quiz_id, responses)
			current_app.logger.info(f"✅ Saved {len(responses)} quiz responses for quiz {quiz_id}")
		except Exception as e:
			current_app.logger.error(f"❌ Error saving quiz responses for quiz {quiz_id}: {str(e)}", exc_info=True)
			return jsonify({"error": "internal_error", "message": f"Failed to save quiz responses: {str(e)}"}), 500
		
		# Save diagnostic to database for authenticated users
		try:
			current_app.logger.info(f"Saving diagnostic for quiz {quiz_id} (user: {current_user_id})")
			diagnostic = _repo().save_ai_diagnostic({
				"quiz_id": quiz_id,
				"analysis_result": analysis,  # Store complete analysis
				"overall_performance": analysis.get("overall_performance"),
				"topic_breakdown": analysis.get("topic_breakdown"),
				"root_cause_analysis": analysis.get("root_cause_analysis"),
				"predicted_jamb_score": analysis.get("predicted_jamb_score"),
				"study_plan": analysis.get("study_plan"),  # Study plan included (Decision 4: Option A)
				"recommendations": analysis.get("recommendations"),
				"analysis_summary": analysis.get("analysis_summary"),  # Include analysis summary
			})
			diagnostic_id = diagnostic.get("id")
			if not diagnostic_id:
				current_app.logger.error(f"❌ Diagnostic saved but no ID returned. Diagnostic data: {diagnostic}")
				return jsonify({"error": "internal_error", "message": "Failed to save diagnostic - no ID returned"}), 500
			current_app.logger.info(f"✅ Saved diagnostic to database: {diagnostic_id} (quiz_id: {quiz_id}, user: {current_user_id})")
		except Exception as e:
			current_app.logger.error(f"❌ Error saving diagnostic for quiz {quiz_id}: {str(e)}", exc_info=True)
			return jsonify({"error": "internal_error", "message": f"Failed to save diagnostic: {str(e)}"}), 500
	else:
		# Guest user: Don't save to database, just generate diagnostic
		current_app.logger.info("Guest user: Diagnostic generated but not saved to database (frontend will store in localStorage)")
		# Generate a temporary diagnostic ID for the response (not saved to DB)
		diagnostic = {
			"id": str(uuid.uuid4()),
			"quiz_id": None,  # No quiz_id for guest users
			"generated_at": datetime.now(timezone.utc).isoformat()
		}
	
	# Prepare response (same structure for both authenticated and guest users)
	response_data = {
		**analysis,
		"id": diagnostic.get("id"),
		"quiz_id": quiz_id,  # Will be None for guest users
		"generated_at": diagnostic.get("generated_at", datetime.now(timezone.utc).isoformat())
	}
	
	# Log response with detailed information
	if is_guest:
		current_app.logger.info(f"✅ Guest diagnostic generated: {response_data.get('id')} (not saved to database)")
		current_app.logger.info(f"📤 Returning guest diagnostic response (quiz_id: None)")
	else:
		diagnostic_id = response_data.get("id")
		current_app.logger.info(f"✅✅✅ SUCCESS: Authenticated diagnostic generated and saved ✅✅✅")
		current_app.logger.info(f"   - Diagnostic ID: {diagnostic_id}")
		current_app.logger.info(f"   - Quiz ID: {quiz_id}")
		current_app.logger.info(f"   - User ID: {current_user_id}")
		current_app.logger.info(f"📤 Returning authenticated diagnostic response (quiz_id: {quiz_id}, diagnostic_id: {diagnostic_id})")
	
	return jsonify(response_data), 200


# Note: Study plan endpoint removed per Decision 4: Option A
# Study plan is now included in the diagnostic analysis response
# To get a study plan, use the /analyze-diagnostic endpoint


@ai_bp.post("/save-diagnostic")
@require_auth
@validate_json(SaveDiagnosticRequest)
def save_diagnostic(current_user_id):
	"""
	Save a guest diagnostic to the database after user signs up.
	
	This endpoint allows users who took a quiz as guests to save their diagnostic
	results to the database after creating an account.
	
	Flow:
	1. Guest user takes quiz -> gets diagnostic (stored in localStorage)
	2. Guest user signs up/logs in
	3. Frontend calls this endpoint to save their diagnostic
	4. Backend creates quiz, saves responses, and saves diagnostic
	5. Returns quiz_id and diagnostic_id for frontend to update localStorage
	"""
	data = request.get_json(force=True) or {}
	
	current_app.logger.info("=" * 60)
	current_app.logger.info(f"💾 SAVE-DIAGNOSTIC REQUEST RECEIVED")
	current_app.logger.info(f"   - User ID: {current_user_id}")
	current_app.logger.info(f"   - Has diagnostic data: {bool(data.get('diagnostic'))}")
	current_app.logger.info(f"   - Has questions_list: {bool(data.get('questions_list'))}")
	current_app.logger.info(f"   - Subject: {data.get('subject')}")
	current_app.logger.info(f"   - Total questions: {data.get('total_questions')}")
	current_app.logger.info("=" * 60)
	
	# Validate required fields (diagnostic is optional - will be regenerated if not provided)
	ok, missing = require_fields(data, ["subject", "total_questions", "time_taken", "questions_list"])
	if not ok:
		current_app.logger.error(f"❌ Missing required fields: {missing}")
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	
	# Ensure user exists in users table (auto-create if needed)
	try:
		user = _repo().get_user(current_user_id)
		if not user:
			# User doesn't exist, create them
			# Try to get email and name from JWT token payload
			email = f"user_{current_user_id[:8]}@example.com"  # Default placeholder
			name = "Student"  # Default name
			
			# Extract user info from JWT token if available
			try:
				auth_header = request.headers.get("Authorization", "")
				if auth_header:
					auth = get_auth()
					if auth:
						user_info = auth.verify_token(auth_header)
						if user_info:
							# Get email from token
							token_email = user_info.get("email")
							if token_email:
								email = token_email
							
							# Try to get name from user metadata
							payload = user_info.get("payload", {})
							if payload:
								user_metadata = payload.get("user_metadata", {})
								if user_metadata and user_metadata.get("name"):
									name = user_metadata.get("name")
								elif payload.get("name"):
									name = payload.get("name")
			except Exception as e:
				current_app.logger.debug(f"Could not extract user info from JWT: {str(e)}")
			
			# Create user in users table
			user = _repo().upsert_user({
				"id": current_user_id,
				"email": email,
				"name": name
			})
			current_app.logger.info(f"Auto-created user in users table: {current_user_id} ({email})")
	except Exception as e:
		current_app.logger.error(f"Error ensuring user exists: {str(e)}", exc_info=True)
		# Continue anyway - the quiz creation will fail with a clearer error if user still doesn't exist
	
	# Create quiz
	try:
		current_app.logger.info(f"Creating quiz for user {current_user_id} from guest diagnostic...")
		quiz = _repo().create_quiz({
			"user_id": current_user_id,
			"subject": data["subject"],
			"total_questions": data["total_questions"],
			"time_taken_minutes": data["time_taken"],
			"completed_at": datetime.now(timezone.utc).isoformat(),
		})
		quiz_id = quiz.get("id")
		if not quiz_id:
			current_app.logger.error(f"❌ Quiz created but no ID returned: {quiz}")
			return jsonify({"error": "internal_error", "message": "Failed to create quiz - no ID returned"}), 500
		current_app.logger.info(f"✅ Created quiz from guest diagnostic: {quiz_id} (user: {current_user_id})")
	except Exception as e:
		current_app.logger.error(f"❌ Error creating quiz from guest diagnostic: {str(e)}", exc_info=True)
		error_str = str(e)
		if "user_id" in error_str and "not present in table" in error_str:
			return jsonify({
				"error": "user_not_found", 
				"message": "User does not exist in database. Please ensure user is registered."
			}), 400
		return jsonify({"error": "internal_error", "message": f"Failed to create quiz: {str(e)}"}), 500
	
	# Prepare quiz responses
	questions_list = data["questions_list"]
	responses = [
		{
			"question_id": None,  # question_id is optional
			"topic": q.get("topic"),
			"student_answer": q.get("student_answer"),
			"correct_answer": q.get("correct_answer"),
			"is_correct": q.get("is_correct"),
			"confidence": q.get("confidence", 3),
			"explanation": q.get("explanation", ""),
			"time_spent_seconds": q.get("time_spent_seconds"),
		}
		for q in questions_list
	]
	
	# Save quiz responses
	try:
		current_app.logger.info(f"Saving {len(responses)} quiz responses for quiz {quiz_id}...")
		_repo().save_quiz_responses(quiz_id, responses)
		current_app.logger.info(f"✅ Saved {len(responses)} quiz responses for quiz {quiz_id}")
	except Exception as e:
		current_app.logger.error(f"❌ Error saving quiz responses: {str(e)}", exc_info=True)
		return jsonify({"error": "internal_error", "message": f"Failed to save quiz responses: {str(e)}"}), 500
	
	# Extract diagnostic data - if not provided, regenerate it from quiz data
	diagnostic_data = data.get("diagnostic")
	diagnostic_regenerated = False
	
	if not diagnostic_data:
		# Diagnostic not provided - regenerate it from quiz data using AI service
		current_app.logger.info(f"⚠️ Diagnostic not provided in request, regenerating from quiz data for quiz: {quiz_id}")
		current_app.logger.info(f"   This will take longer but ensures diagnostic is saved correctly")
		diagnostic_regenerated = True
		try:
			# Use the analyze-diagnostic logic to generate diagnostic
			from ..services.ai_enhanced import EnhancedAIService
			cfg = current_app.config
			ai_service = EnhancedAIService(
				api_key=cfg.get("GOOGLE_API_KEY"),
				model_name=cfg.get("AI_MODEL_NAME", "gemini-1.5-flash"),
				mock=cfg.get("AI_MOCK", True)
			)
			
			# Prepare quiz data for analysis
			quiz_data = {
				"subject": data["subject"],
				"total_questions": data["total_questions"],
				"time_taken": data["time_taken"],
				"questions_list": questions_list
			}
			
			# Generate diagnostic
			current_app.logger.info(f"Calling AI service to regenerate diagnostic...")
			diagnostic_result = ai_service.analyze_diagnostic(quiz_data)
			
			if not diagnostic_result:
				current_app.logger.error("❌ Failed to generate diagnostic from quiz data")
				return jsonify({"error": "internal_error", "message": "Failed to generate diagnostic"}), 500
			
			diagnostic_data = diagnostic_result
			current_app.logger.info(f"✅ Successfully regenerated diagnostic for quiz: {quiz_id}")
		except Exception as e:
			current_app.logger.error(f"❌ Error regenerating diagnostic: {str(e)}", exc_info=True)
			return jsonify({"error": "internal_error", "message": f"Failed to generate diagnostic: {str(e)}"}), 500
	else:
		current_app.logger.info(f"✅ Using provided diagnostic data from guest quiz for quiz: {quiz_id}")
		current_app.logger.info(f"   Diagnostic ID in data: {diagnostic_data.get('id') if isinstance(diagnostic_data, dict) else 'N/A'}")
	
	# Save diagnostic to database
	try:
		current_app.logger.info(f"Saving diagnostic to database for quiz {quiz_id}...")
		diagnostic = _repo().save_ai_diagnostic({
			"quiz_id": quiz_id,
			"analysis_result": diagnostic_data,  # Store complete diagnostic as analysis_result
			"overall_performance": diagnostic_data.get("overall_performance"),
			"topic_breakdown": diagnostic_data.get("topic_breakdown"),
			"root_cause_analysis": diagnostic_data.get("root_cause_analysis"),
			"predicted_jamb_score": diagnostic_data.get("predicted_jamb_score"),
			"study_plan": diagnostic_data.get("study_plan"),
			"recommendations": diagnostic_data.get("recommendations"),
		})
		diagnostic_id = diagnostic.get("id")
		if not diagnostic_id:
			current_app.logger.error(f"❌ Diagnostic saved but no ID returned: {diagnostic}")
			return jsonify({"error": "internal_error", "message": "Failed to save diagnostic - no ID returned"}), 500
		current_app.logger.info(f"✅✅✅ GUEST DIAGNOSTIC SAVED SUCCESSFULLY ✅✅✅")
		current_app.logger.info(f"   - Diagnostic ID: {diagnostic_id}")
		current_app.logger.info(f"   - Quiz ID: {quiz_id}")
		current_app.logger.info(f"   - User ID: {current_user_id}")
		current_app.logger.info(f"   - Diagnostic regenerated: {diagnostic_regenerated}")
		current_app.logger.info("=" * 60)
	except Exception as e:
		current_app.logger.error(f"❌ Error saving diagnostic: {str(e)}", exc_info=True)
		return jsonify({"error": "internal_error", "message": f"Failed to save diagnostic: {str(e)}"}), 500
	
	# Return quiz_id for frontend to update localStorage
	return jsonify({
		"quiz_id": quiz_id,
		"diagnostic_id": diagnostic_id,
		"message": "Diagnostic saved successfully",
		"diagnostic_regenerated": diagnostic_regenerated  # Indicate if diagnostic was regenerated
	}), 200


@ai_bp.post("/explain-answer")
@require_auth
def explain_answer(current_user_id):
	"""Explain answer - requires authentication (Decision 11: Option A)"""
	data = request.get_json(force=True) or {}
	ok, missing = require_fields(data, ["questionId", "studentAnswer", "correctAnswer", "studentReasoning"])
	if not ok:
		return jsonify({"error": "missing_fields", "fields": missing}), 400
	try:
		# Note: Using legacy AI service for explain_answer (not yet migrated to enhanced service)
		from ..services.ai import AIService
		cfg = current_app.config
		legacy_ai = AIService(
			cfg.get("GOOGLE_API_KEY"), 
			cfg.get("AI_MODEL_NAME", "gemini-2.0-flash"), 
			cfg.get("AI_MOCK", "true").lower() == "true"
		)
		explanation = legacy_ai.explain_answer({
			"questionId": data["questionId"],
			"studentAnswer": data["studentAnswer"],
			"correctAnswer": data["correctAnswer"],
			"studentReasoning": data["studentReasoning"],
		})
	except AIAPIError as e:
		return jsonify({"error": "ai_service_error", "message": e.message}), e.status_code
	except Exception as e:
		current_app.logger.error(f"Error in explain_answer: {str(e)}", exc_info=True)
		return jsonify({"error": "internal_error", "message": "An unexpected error occurred while explaining answer"}), 500
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


