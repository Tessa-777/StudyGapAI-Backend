from typing import Any, Dict, List, Optional

from supabase import create_client, Client

from .interface import Repository


class SupabaseRepository(Repository):
	def __init__(self, url: str, key: str) -> None:
		self.client: Client = create_client(url, key)

	# Users
	def upsert_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
		# Upsert operation - Supabase returns data automatically
		try:
			response = self.client.table("users").upsert(user).execute()
			# If data is returned, use it
			if response.data and len(response.data) > 0:
				return response.data[0]
		except Exception:
			pass  # Fall through to query by email
		
		# Fallback: query the user by email to get full data
		email = user.get("email")
		if email:
			user_data = self.get_user_by_email(email)
			if user_data:
				return user_data
		
		# Last resort: return user dict (will have generated ID from database)
		# Generate a UUID if not present
		if "id" not in user:
			import uuid
			user["id"] = str(uuid.uuid4())
		return user

	def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
		response = self.client.table("users").select("*").eq("id", user_id).maybe_single().execute()
		return response.data

	def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
		response = (
			self.client.table("users").select("*").eq("email", email).maybe_single().execute()
		)
		return response.data

	def update_user_target_score(self, user_id: str, target_score: int) -> Dict[str, Any]:
		response = (
			self.client.table("users")
			.update({"target_score": target_score})
			.eq("id", user_id)
			.execute()
		)
		if response.data and len(response.data) > 0:
			return response.data[0]
		# Fallback: query the user
		user = self.get_user(user_id)
		if user:
			return user
		raise KeyError(f"User {user_id} not found")

	# Questions / Quizzes
	def get_diagnostic_questions(self, total: int = 30) -> List[Dict[str, Any]]:
		response = (
			self.client.table("questions")
			.select("*")
			.limit(total)
			.execute()
		)
		return response.data

	def create_quiz(self, quiz: Dict[str, Any]) -> Dict[str, Any]:
		response = self.client.table("diagnostic_quizzes").insert(quiz).execute()
		if response.data and len(response.data) > 0:
			return response.data[0]
		# Fallback: return quiz dict with generated ID
		return quiz

	def save_quiz_responses(self, quiz_id: str, responses: List[Dict[str, Any]]) -> None:
		self.client.table("quiz_responses").insert(responses).execute()

		# compute quiz summary
		res = (
			self.client.table("quiz_responses")
			.select("is_correct")
			.eq("quiz_id", quiz_id)
			.execute()
		)
		correct = sum(1 for r in res.data if r.get("is_correct"))
		total = len(res.data)
		score = (correct / max(1, total)) * 100.0
		self.client.table("diagnostic_quizzes").update({
			"correct_answers": correct,
			"score_percentage": score,
		}).eq("id", quiz_id).execute()

	def get_quiz_results(self, quiz_id: str) -> Dict[str, Any]:
		quiz = (
			self.client.table("diagnostic_quizzes").select("*").eq("id", quiz_id).single().execute().data
		)
		responses = (
			self.client.table("quiz_responses").select("*").eq("quiz_id", quiz_id).execute().data
		)
		return {"quiz": quiz, "responses": responses}

	# AI Diagnostics / Study Plans
	def save_ai_diagnostic(self, diagnostic: Dict[str, Any]) -> Dict[str, Any]:
		payload = {**diagnostic}
		if "generated_at" not in payload:
			from datetime import datetime, timezone
			payload["generated_at"] = datetime.now(timezone.utc).isoformat()
		response = self.client.table("ai_diagnostics").insert(payload).execute()
		if response.data and len(response.data) > 0:
			return response.data[0]
		return payload

	def create_study_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
		from datetime import datetime, timezone
		now = datetime.now(timezone.utc).isoformat()
		payload = {**plan}
		payload.setdefault("created_at", now)
		payload.setdefault("updated_at", now)
		response = self.client.table("study_plans").insert(payload).execute()
		if response.data and len(response.data) > 0:
			return response.data[0]
		return payload

	def update_study_plan(self, plan_id: str, plan_data: Dict[str, Any]) -> Dict[str, Any]:
		from datetime import datetime, timezone
		response = (
			self.client.table("study_plans")
			.update({"plan_data": plan_data, "updated_at": datetime.now(timezone.utc).isoformat()})
			.eq("id", plan_id)
			.execute()
		)
		if response.data and len(response.data) > 0:
			return response.data[0]
		# Fallback: return updated plan data
		plan = self.get_study_plan(plan_id)
		if plan:
			return plan
		return {"id": plan_id, "plan_data": plan_data}

	def get_study_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
		response = self.client.table("study_plans").select("*").eq("id", plan_id).maybe_single().execute()
		return response.data

	# Progress
	def get_user_progress(self, user_id: str) -> List[Dict[str, Any]]:
		response = (
			self.client.table("progress_tracking").select("*").eq("user_id", user_id).execute()
		)
		return response.data

	def mark_progress_complete(self, progress: Dict[str, Any]) -> Dict[str, Any]:
		response = self.client.table("progress_tracking").insert(progress).execute()
		if response.data and len(response.data) > 0:
			return response.data[0]
		return progress

	# Analytics
	def get_analytics_dashboard(self) -> Dict[str, Any]:
		# This can be optimized via SQL views; simple version here
		users = self.client.table("users").select("id").execute().data
		quizzes = self.client.table("diagnostic_quizzes").select("score_percentage").execute().data
		avg_score = (
			sum(q.get("score_percentage", 0.0) for q in quizzes) / max(1, len(quizzes))
		)
		return {
			"total_users": len(users),
			"total_quizzes": len(quizzes),
			"avg_score": avg_score,
		}


