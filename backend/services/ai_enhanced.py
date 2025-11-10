"""
Enhanced AI Service for AI/SE Integration
Implements structured output, validation, and comprehensive diagnostic analysis
"""

import os
import hashlib
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone
from flask import current_app
import requests

from .ai_prompts import SYSTEM_INSTRUCTION, build_user_prompt
from .ai_schemas import RESPONSE_SCHEMA, VALID_ERROR_TYPES, VALID_TOPIC_STATUSES
from .confidence_inference import add_confidence_scores
from ..utils.calculations import (
	validate_and_correct_fluency_index,
	validate_and_correct_jamb_score,
	validate_and_correct_overall_performance,
	validate_topic_status,
	validate_error_type,
	calculate_jamb_base_score
)


class AIAPIError(Exception):
	"""Custom exception for AI API errors with HTTP status code"""
	def __init__(self, message: str, status_code: int = 503):
		self.message = message
		self.status_code = status_code
		super().__init__(message)


class EnhancedAIService:
	"""
	Enhanced AI Service with structured output and validation.
	Implements AI/SE diagnostic analysis with comprehensive validation.
	"""
	
	def __init__(self, api_key: str | None, model_name: str, mock: bool) -> None:
		"""
		Initialize Enhanced AI Service.
		
		Args:
			api_key: Gemini API key
			model_name: Model name (e.g., 'gemini-2.0-flash')
			mock: Whether to use mock mode
		"""
		# IMPORTANT: Only use mock if explicitly requested OR if API key is missing
		# If mock=False and api_key exists, use real AI
		if mock:
			self.mock = True
		elif not api_key:
			self.mock = True
			# Log warning if API key is missing
			try:
				if current_app:
					current_app.logger.warning("⚠️ API key is missing - forcing mock mode even though mock=False")
			except:
				pass
		else:
			self.mock = False
		
		self.model_name = model_name
		self.api_key = api_key
		self.base_url = "https://generativelanguage.googleapis.com/v1beta"
		
		# Log initialization
		try:
			if current_app:
				current_app.logger.info(f"EnhancedAIService: mock={self.mock}, model={self.model_name}, has_api_key={bool(self.api_key)}")
		except:
			pass

	def _mock_analysis(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Generate realistic mock analysis data matching new format.
		Decision 12: Option A - Realistic mock data
		
		Args:
			quiz_data: Quiz data dictionary
			
		Returns:
			Mock analysis result matching RESPONSE_SCHEMA
		"""
		questions_list = quiz_data.get("questions_list", [])
		total_questions = len(questions_list)
		correct_answers = sum(1 for q in questions_list if q.get("is_correct", False))
		accuracy = (correct_answers / total_questions * 100.0) if total_questions > 0 else 0.0
		time_taken = quiz_data.get("time_taken", 0)
		
		# Calculate average confidence
		confidences = [q.get("confidence", 3) for q in questions_list]
		avg_confidence = sum(confidences) / len(confidences) if confidences else 3.0
		
		# Group by topic
		topic_stats = {}
		for q in questions_list:
			topic = q.get("topic", "Unknown")
			if topic not in topic_stats:
				topic_stats[topic] = {"total": 0, "correct": 0, "confidences": []}
			topic_stats[topic]["total"] += 1
			if q.get("is_correct", False):
				topic_stats[topic]["correct"] += 1
			topic_stats[topic]["confidences"].append(q.get("confidence", 3))
		
		# Build topic breakdown
		topic_breakdown = []
		for topic, stats in topic_stats.items():
			topic_accuracy = (stats["correct"] / stats["total"] * 100.0) if stats["total"] > 0 else 0.0
			topic_avg_confidence = sum(stats["confidences"]) / len(stats["confidences"]) if stats["confidences"] else 3.0
			fluency_index = (topic_accuracy / 100.0) * (topic_avg_confidence / 5.0) * 100.0
			
			# Determine status
			if fluency_index < 50 or topic_accuracy < 60:
				status = "weak"
				severity = "critical" if topic_accuracy < 40 else "moderate"
			elif fluency_index <= 70 or topic_accuracy <= 75:
				status = "developing"
				severity = "moderate"
			else:
				status = "strong"
				severity = None
			
			topic_breakdown.append({
				"topic": f"{quiz_data.get('subject', 'Mathematics')}: {topic}",
				"accuracy": round(topic_accuracy, 2),
				"fluency_index": round(fluency_index, 2),
				"status": status,
				"questions_attempted": stats["total"],
				"severity": severity,
				"dominant_error_type": "conceptual_gap" if status == "weak" else "knowledge_gap"
			})
		
		# Calculate JAMB score
		base_score = (accuracy / 100.0) * 400.0
		projected_score = max(0, min(400, round(base_score)))
		
		# Build error distribution
		error_distribution = {
			"conceptual_gap": sum(1 for q in questions_list if not q.get("is_correct", False) and "concept" in q.get("explanation", "").lower()),
			"procedural_error": 0,
			"careless_mistake": sum(1 for q in questions_list if not q.get("is_correct", False) and q.get("confidence", 3) >= 4),
			"knowledge_gap": sum(1 for q in questions_list if not q.get("is_correct", False) and len(q.get("explanation", "")) < 20),
			"misinterpretation": 0
		}
		
		# Find primary weakness
		primary_weakness = max(error_distribution.items(), key=lambda x: x[1])[0] if any(error_distribution.values()) else "knowledge_gap"
		
		# Generate 6-week study plan
		weekly_schedule = []
		weak_topics = [t["topic"] for t in topic_breakdown if t["status"] == "weak"]
		
		for week in range(1, 7):
			if week <= len(weak_topics):
				focus_topic = weak_topics[week - 1]
				focus = f"{focus_topic}: Core Concepts & Practice"
			elif week == 6:
				focus = "Full Exam Simulation & Review"
			else:
				focus = "Review & Advanced Topics"
			
			weekly_schedule.append({
				"week": week,
				"focus": focus,
				"study_hours": 8 if week <= 3 else 6,
				"key_activities": [
					f"Review {focus_topic if week <= len(weak_topics) else 'all topics'}",
					"Complete practice problems",
					"Take mini-quiz" if week % 2 == 0 else "Review notes"
				]
			})
		
		# Build recommendations
		recommendations = []
		if weak_topics:
			recommendations.append({
				"priority": 1,
				"category": "weakness",
				"action": f"Focus on {weak_topics[0]} for the next 2 weeks",
				"rationale": f"Your lowest performing topic needs immediate attention"
			})
		
		# Generate analysis summary (in second person for frontend display)
		weak_count = len([t for t in topic_breakdown if t["status"] == "weak"])
		summary_parts = []
		if accuracy < 60:
			summary_parts.append(f"Your performance shows significant gaps with {accuracy:.1f}% accuracy.")
		elif accuracy < 75:
			summary_parts.append(f"Your performance is developing with {accuracy:.1f}% accuracy.")
		else:
			summary_parts.append(f"You demonstrated strong performance with {accuracy:.1f}% accuracy.")
		
		if weak_count > 0:
			summary_parts.append(f"You have {weak_count} weak topic(s) requiring focused attention.")
		
		if primary_weakness:
			weakness_names = {
				"conceptual_gap": "conceptual understanding",
				"procedural_error": "procedural application",
				"careless_mistake": "attention to detail",
				"knowledge_gap": "foundational knowledge",
				"misinterpretation": "question interpretation"
			}
			weakness_name = weakness_names.get(primary_weakness, primary_weakness)
			summary_parts.append(f"Your primary weakness is in {weakness_name}.")
		
		analysis_summary = " ".join(summary_parts) if summary_parts else f"Your diagnostic analysis shows an overall accuracy of {accuracy:.1f}%."
		
		return {
			"overall_performance": {
				"accuracy": round(accuracy, 2),
				"total_questions": total_questions,
				"correct_answers": correct_answers,
				"avg_confidence": round(avg_confidence, 2),
				"time_per_question": round((time_taken * 60) / total_questions, 2) if total_questions > 0 else 0.0
			},
			"topic_breakdown": topic_breakdown,
			"root_cause_analysis": {
				"primary_weakness": primary_weakness,
				"error_distribution": error_distribution
			},
			"predicted_jamb_score": {
				"score": projected_score,
				"confidence_interval": "± 25 points"
			},
			"study_plan": {
				"weekly_schedule": weekly_schedule
			},
			"recommendations": recommendations,
			"analysis_summary": analysis_summary
		}

	def analyze_diagnostic(self, quiz_data: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Analyze diagnostic quiz data using Gemini structured output.
		
		Args:
			quiz_data: Dictionary with keys: subject, total_questions, time_taken, questions_list
			
		Returns:
			Complete diagnostic analysis matching RESPONSE_SCHEMA
			
		Raises:
			AIAPIError: If AI analysis fails
			ValueError: If response validation fails
		"""
		# Note: Confidence scores should be added before calling this method (in the route)
		# But we add it here as a safety measure if not already done
		questions_list = quiz_data.get("questions_list", [])
		if any(q.get("confidence") is None for q in questions_list):
			quiz_data = quiz_data.copy()
			quiz_data["questions_list"] = add_confidence_scores(questions_list)
		
		if self.mock:
			# Log that we're using mock mode
			try:
				if current_app:
					current_app.logger.info("📊 Using mock analysis (mock mode enabled)")
			except:
				pass
			return self._mock_analysis(quiz_data)
		
		# Log that we're calling real AI
		try:
			if current_app:
				current_app.logger.info(f"🤖 Calling Gemini API: model={self.model_name}, api_key_present={bool(self.api_key)}")
		except:
			pass
		
		# Check cache (Decision 13: Option A - Cache by input hash)
		cache = None
		try:
			if current_app:
				cache = current_app.extensions.get("cache_instance")
		except (RuntimeError, AttributeError):
			pass
		
		cache_key = None
		if cache:
			cache_key = f"ai:analyze:{hashlib.sha256(json.dumps(quiz_data, sort_keys=True).encode()).hexdigest()}"
			cached = cache.get(cache_key)
			if cached:
				# Log cache hit
				try:
					if current_app:
						current_app.logger.info("📦 Cache hit - returning cached analysis (no API call)")
				except:
					pass
				return cached
			else:
				# Log cache miss
				try:
					if current_app:
						current_app.logger.info("📦 Cache miss - will make API call")
				except:
					pass
		
		# Fetch topics from repository to include in prompt
		topics_data = None
		try:
			if current_app:
				repo = current_app.extensions.get("repository")
				if repo:
					# Get all topics for the subject
					subject = quiz_data.get("subject", "Mathematics")
					topics = repo.get_topics(subject=subject)
					
					# Format topics with prerequisites (prerequisite_topics is text[] array of topic names)
					if topics:
						topics_data = []
						for topic in topics:
							# prerequisite_topics is a text[] array containing topic names directly
							prerequisite_topics = topic.get("prerequisite_topics", [])
							
							# Ensure it's a list (Supabase returns arrays as lists)
							if not isinstance(prerequisite_topics, list):
								prerequisite_topics = []
							
							# Add topic with prerequisites (already topic names, no resolution needed)
							topics_data.append({
								"name": topic.get("name", "Unknown"),
								"jamb_weight": topic.get("jamb_weight", 0.0),
								"prerequisites": prerequisite_topics  # Direct topic names from text[] array
							})
						
						# Log topics inclusion
						current_app.logger.info(f"📚 Including {len(topics_data)} topics with prerequisites in prompt")
		except Exception as e:
			# If topics fetch fails, continue without them (non-critical)
			try:
				if current_app:
					current_app.logger.warning(f"⚠️ Failed to fetch topics for prompt: {str(e)}")
			except:
				pass
		
		# Build prompt with system instruction and topics data
		user_prompt = build_user_prompt(quiz_data, topics_data=topics_data)
		
		# Combine system instruction and user prompt
		full_prompt = f"{SYSTEM_INSTRUCTION}\n\n{user_prompt}\n\nRemember: Return ONLY valid JSON matching the required schema. No markdown, no code blocks, no explanations outside JSON."
		
		# Call Gemini API via REST with structured output
		text = self._call_gemini_api_structured(full_prompt)
		
		if not text:
			raise AIAPIError("Empty response from Gemini API", 503)
		
		# Parse JSON
		try:
			result = json.loads(text)
		except json.JSONDecodeError as e:
			raise ValueError(f"Failed to parse JSON from Gemini response: {str(e)}")
		
		# Validate and correct response (Decision 7: Option B, Decision 8: Option B)
		result = self._validate_and_correct_response(result, quiz_data)
		
		# Cache result
		if cache and cache_key:
			cache.set(cache_key, result, timeout=300)
		
		return result

	def _call_gemini_api_structured(self, prompt: str) -> str:
		"""
		Call Gemini API via REST with structured output support.
		
		Note: Gemini REST API v1beta supports responseSchema for structured output.
		
		Args:
			prompt: Complete prompt including system instruction
			
		Returns:
			Response text (JSON string)
			
		Raises:
			AIAPIError: If API call fails
		"""
		url = f"{self.base_url}/models/{self.model_name}:generateContent"
		headers = {
			"Content-Type": "application/json",
		}
		params = {"key": self.api_key}
		
		# Build payload with structured output configuration
		payload = {
			"contents": [{
				"parts": [{"text": prompt}]
			}],
			"generationConfig": {
				"responseMimeType": "application/json",
				"responseSchema": RESPONSE_SCHEMA
			}
		}
		
		try:
			# Log API call attempt
			try:
				if current_app:
					current_app.logger.info(f"📡 Calling Gemini API: {url} (model: {self.model_name})")
			except:
				pass
			
			# Increase timeout for complex diagnostic analysis (90 seconds)
			# This gives more time for structured output generation
			response = requests.post(url, json=payload, headers=headers, params=params, timeout=90)
			
			# Log response status
			try:
				if current_app:
					current_app.logger.info(f"📥 Gemini API response: Status {response.status_code}")
			except:
				pass
			
			# Check status before raising
			if response.status_code != 200:
				# Get detailed error message
				try:
					error_data = response.json()
					
					# Check if error is at top level (e.g., {"error": "ERROR_USER_ABORTED_REQUEST", "details": {...}})
					top_level_error = error_data.get("error")
					if isinstance(top_level_error, str) and "USER_ABORTED_REQUEST" in top_level_error.upper():
						# This is the format the user is seeing
						details = error_data.get("details", {})
						detail_msg = details.get("detail", "") if isinstance(details, dict) else details.get("title", "")
						
						if detail_msg:
							user_friendly_msg = f"The AI analysis request was interrupted: {detail_msg}. Please try again."
						else:
							user_friendly_msg = "The AI analysis request was interrupted. This may happen if the request takes too long. Please try again."
						
						if current_app:
							current_app.logger.warning(f"Gemini API request aborted: {top_level_error}")
							current_app.logger.warning(f"Error details: {details}")
						raise AIAPIError(user_friendly_msg, 408)
					
					# Otherwise, try nested error structure
					error_obj = error_data.get("error", {})
					if isinstance(error_obj, str):
						error_msg = error_obj
						error_code = response.status_code
						error_type = ""
					else:
						error_msg = error_obj.get("message", str(error_data))
						error_code = error_obj.get("code", response.status_code)
						error_type = error_obj.get("status", "")
					
					# Check for specific error types in nested structure
					# Handle ERROR_USER_ABORTED_REQUEST in various formats
					error_str = str(error_data).upper()
					has_abort_error = (
						"USER_ABORTED_REQUEST" in error_msg.upper() or
						"USER_ABORTED_REQUEST" in error_str or
						"ERROR_USER_ABORTED_REQUEST" in error_str or
						top_level_error == "ERROR_USER_ABORTED_REQUEST"
					)
					
					if has_abort_error:
						# Request was aborted - could be timeout or user cancellation
						# Extract details if available
						details = error_data.get("details", {})
						detail_msg = details.get("detail", "") if isinstance(details, dict) else ""
						
						if detail_msg:
							user_friendly_msg = f"The AI analysis request was interrupted: {detail_msg}. Please try again."
						else:
							user_friendly_msg = "The AI analysis request was interrupted. This may happen if the request takes too long. Please try again with a smaller quiz or wait a moment and retry."
						
						if current_app:
							current_app.logger.warning(f"Gemini API request aborted: {error_msg}")
							current_app.logger.warning(f"Error details: {details}")
							current_app.logger.warning(f"Full error: {error_data}")
						raise AIAPIError(user_friendly_msg, 408)  # 408 Request Timeout
					
					# Log full error for debugging
					if current_app:
						current_app.logger.error(f"Gemini API error (Status {response.status_code}): {error_msg}")
						current_app.logger.error(f"Error type: {error_type}, Code: {error_code}")
						current_app.logger.error(f"Full error response: {error_data}")
						current_app.logger.error(f"Request URL: {url}")
						current_app.logger.error(f"Model: {self.model_name}")
					
					# Raise with detailed error
					raise AIAPIError(
						f"Gemini API error (Status {response.status_code}): {error_msg}", 
						response.status_code
					)
				except AIAPIError:
					# Re-raise AIAPIError as-is
					raise
				except (ValueError, KeyError, json.JSONDecodeError):
					# If can't parse error, raise with response text
					error_msg = response.text[:500]
					if current_app:
						current_app.logger.error(f"Gemini API error (Status {response.status_code}): {error_msg}")
					
					# Check if it's an aborted request even if we can't parse JSON
					if "abort" in error_msg.lower() or "timeout" in error_msg.lower():
						raise AIAPIError(
							"The AI analysis request was interrupted or timed out. Please try again.",
							408
						)
					
					raise AIAPIError(
						f"Gemini API error (Status {response.status_code}): {error_msg}",
						response.status_code
					)
			
			response.raise_for_status()  # This should not raise if status is 200
			data = response.json()
			
			# Extract text from response
			if "candidates" in data and len(data["candidates"]) > 0:
				candidate = data["candidates"][0]
				if "content" in candidate and "parts" in candidate["content"]:
					if len(candidate["content"]["parts"]) > 0:
						text = candidate["content"]["parts"][0].get("text", "")
						# Clean text - remove markdown code blocks if present
						text = text.strip()
						if text.startswith('```json'):
							text = text[7:]
						if text.startswith('```'):
							text = text[3:]
						if text.endswith('```'):
							text = text[:-3]
						return text.strip()
			
			raise ValueError(f"Unexpected response format: {data}")
			
		except requests.exceptions.Timeout as e:
			# Handle timeout errors specifically
			if current_app:
				current_app.logger.error(f"Gemini API timeout: Request took longer than 60 seconds")
			raise AIAPIError(
				"The AI analysis request timed out. The request is taking too long to process. Please try again or reduce the number of questions.",
				408
			)
		except requests.exceptions.ConnectionError as e:
			# Handle connection errors
			if current_app:
				current_app.logger.error(f"Gemini API connection error: {str(e)}")
			raise AIAPIError(
				"Failed to connect to the AI service. Please check your internet connection and try again.",
				503
			)
		except requests.exceptions.RequestException as e:
			# Handle other request exceptions
			if current_app:
				current_app.logger.error(f"Gemini API request error: {str(e)}")
			# Check if it's an abort/timeout
			if "abort" in str(e).lower() or "timeout" in str(e).lower():
				raise AIAPIError(
					"The AI analysis request was interrupted. Please try again.",
					408
				)
			raise AIAPIError(
				f"AI service request error: {str(e)}",
				503
			)
		except requests.exceptions.HTTPError as e:
			error_code = None
			error_message = ""
			if e.response:
				error_code = e.response.status_code
				try:
					error_data = e.response.json()
					# Extract detailed error message
					if isinstance(error_data, dict):
						error_obj = error_data.get("error", {})
						error_message = error_obj.get("message", str(error_data))
						
						# Check for USER_ABORTED_REQUEST in error data (various formats)
						error_str = str(error_data).upper()
						has_abort_error = (
							"USER_ABORTED_REQUEST" in error_message.upper() or
							"USER_ABORTED_REQUEST" in error_str or
							"ERROR_USER_ABORTED_REQUEST" in error_str or
							error_data.get("error") == "ERROR_USER_ABORTED_REQUEST"
						)
						
						if has_abort_error:
							# Extract details if available
							details = error_data.get("details", {})
							detail_msg = details.get("detail", "") if isinstance(details, dict) else ""
							
							if detail_msg:
								user_msg = f"The AI analysis request was interrupted: {detail_msg}. Please try again."
							else:
								user_msg = "The AI analysis request was interrupted. This may happen if the request takes too long. Please try again."
							
							if current_app:
								current_app.logger.warning(f"Gemini API request aborted: {error_message}")
								current_app.logger.warning(f"Error details: {details}")
							raise AIAPIError(user_msg, 408)
						
						if not error_message:
							error_message = str(error_data)
					else:
						error_message = str(error_data)
				except AIAPIError:
					# Re-raise if we already raised AIAPIError for aborted request
					raise
				except:
					error_message = e.response.text or str(e)
			else:
				error_message = str(e)
			
			# Log detailed error for debugging
			if current_app:
				current_app.logger.error(f"Gemini API error: Status {error_code}, Model: {self.model_name}, URL: {url}, Error: {error_message}")
			
			# Decision 14: Option A - Return errors, no retry
			if error_code == 429 or '429' in error_message or 'RESOURCE_EXHAUSTED' in error_message.upper():
				raise AIAPIError("AI service rate limit exceeded. Please try again later.", 429)
			elif error_code == 503 or '503' in error_message or 'UNAVAILABLE' in error_message.upper():
				raise AIAPIError("AI service temporarily unavailable. Please try again later.", 503)
			else:
				# Include more details in error message
				detailed_error = f"AI service error (Status {error_code}): {error_message}"
				raise AIAPIError(detailed_error, error_code or 503)
		except Exception as e:
			error_message = str(e)
			if '429' in error_message or 'RESOURCE_EXHAUSTED' in error_message.upper():
				raise AIAPIError("AI service rate limit exceeded. Please try again later.", 429)
			elif '503' in error_message or 'UNAVAILABLE' in error_message.upper():
				raise AIAPIError("AI service temporarily unavailable. Please try again later.", 503)
			else:
				raise AIAPIError(f"AI service error: {error_message}", 503)

	def _validate_and_correct_response(self, result: Dict[str, Any], quiz_data: Dict[str, Any]) -> Dict[str, Any]:
		"""
		Validate and correct AI response.
		
		Decision 7: Option B - Validate Fluency Index calculations
		Decision 8: Option B - Recalculate JAMB score
		Decision 6: Option A - Strict error type validation
		Decision 15: Option C - Strict validation with helpful error messages
		
		Args:
			result: AI response dictionary
			quiz_data: Original quiz data for validation
			
		Returns:
			Validated and corrected response
		"""
		questions_list = quiz_data.get("questions_list", [])
		time_taken = quiz_data.get("time_taken", 0)
		subject = quiz_data.get("subject", "Mathematics")
		
		# Validate overall_performance
		if "overall_performance" not in result:
			raise ValueError("Missing 'overall_performance' in AI response")
		
		# Fix Issue 2: Validate and recalculate overall_performance from actual quiz data
		result["overall_performance"] = validate_and_correct_overall_performance(
			result["overall_performance"],
			questions_list,
			time_taken
		)
		
		# Get corrected overall_accuracy for JAMB score calculation
		overall_perf = result["overall_performance"]
		overall_accuracy = overall_perf.get("accuracy", 0)
		
		# Validate and correct topic_breakdown
		if "topic_breakdown" not in result:
			raise ValueError("Missing 'topic_breakdown' in AI response")
		
		# Verify Gemini returned exactly 5 topics (as instructed in prompt)
		topic_count = len(result["topic_breakdown"])
		if topic_count != 5:
			try:
				if current_app:
					current_app.logger.warning(f"⚠️ Gemini returned {topic_count} topics instead of 5. Expected exactly 5 main topics.")
			except:
				pass
		
		# ENFORCE EXACTLY 5 TOPICS - aggregate all topics into the 5 main topics
		from backend.utils.topic_mapping import enforce_five_topics
		result["topic_breakdown"] = enforce_five_topics(
			result["topic_breakdown"],
			questions_list
		)
		
		# Verify we have exactly 5 topics
		if len(result["topic_breakdown"]) != 5:
			try:
				if current_app:
					current_app.logger.error(f"❌ CRITICAL: enforce_five_topics returned {len(result['topic_breakdown'])} topics instead of 5!")
			except:
				pass
			# Force exactly 5 by taking first 5 or padding
			if len(result["topic_breakdown"]) > 5:
				result["topic_breakdown"] = result["topic_breakdown"][:5]
			elif len(result["topic_breakdown"]) < 5:
				# This shouldn't happen, but pad if needed
				from backend.utils.topic_mapping import MAIN_TOPICS
				existing_topics = {t.get("topic", "") for t in result["topic_breakdown"]}
				for main_topic in MAIN_TOPICS:
					if main_topic not in existing_topics and len(result["topic_breakdown"]) < 5:
						result["topic_breakdown"].append({
							"topic": main_topic,
							"accuracy": 0.0,
							"fluency_index": 0.0,
							"status": "weak",
							"questions_attempted": 0,
							"severity": None,
							"dominant_error_type": None
						})
		
		# Validate and correct each topic in breakdown
		corrected_breakdown = []
		for topic in result["topic_breakdown"]:
			# Clean topic name - remove "Subject: " prefix if present (Gemini should return just topic name)
			topic_name = topic.get("topic", "")
			if ":" in topic_name:
				topic["topic"] = topic_name.split(":")[-1].strip()
			
			# Fix Issue 4: Validate and correct Fluency Index (ensures it's always a number)
			corrected_topic = validate_and_correct_fluency_index(topic, questions_list)
			
			# Validate and correct status
			corrected_topic["status"] = validate_topic_status(corrected_topic)
			
			# Validate error types (field is optional, so remove if invalid)
			if corrected_topic.get("dominant_error_type"):
				try:
					corrected_topic["dominant_error_type"] = validate_error_type(corrected_topic["dominant_error_type"])
				except ValueError:
					# Remove field if invalid (field is optional in schema)
					corrected_topic.pop("dominant_error_type", None)
			
			# Validate severity (field is optional)
			if corrected_topic.get("severity") and corrected_topic["severity"] not in ["critical", "moderate", "mild"]:
				# Remove field if invalid (field is optional in schema)
				corrected_topic.pop("severity", None)
			
			corrected_breakdown.append(corrected_topic)
		
		result["topic_breakdown"] = corrected_breakdown
		
		# Validate and correct root_cause_analysis
		if "root_cause_analysis" not in result:
			raise ValueError("Missing 'root_cause_analysis' in AI response")
		
		rca = result["root_cause_analysis"]
		
		# Validate error_distribution first
		error_dist = rca.get("error_distribution", {})
		validated_dist = {}
		for error_type in VALID_ERROR_TYPES:
			count = error_dist.get(error_type, 0)
			if not isinstance(count, int) or count < 0:
				count = 0
			validated_dist[error_type] = count
		
		# If error_distribution is empty or all zeros, calculate from questions
		# This ensures the graph always has data to display
		if not any(validated_dist.values()):
			from backend.utils.error_analysis import calculate_error_distribution
			try:
				calculated_dist = calculate_error_distribution(questions_list)
				# Use calculated distribution if it has data
				if any(calculated_dist.values()):
					validated_dist = calculated_dist
					if current_app:
						current_app.logger.info(f"📊 Calculated error_distribution from questions: {validated_dist}")
				else:
					# If calculation still gives all zeros, check if there are incorrect answers
					# If there are incorrect answers but no classification, default all to knowledge_gap
					incorrect_answers = [q for q in questions_list if not q.get("is_correct", False)]
					if incorrect_answers:
						# Default case: classify all incorrect answers as knowledge_gap
						validated_dist["knowledge_gap"] = len(incorrect_answers)
						if current_app:
							current_app.logger.info(f"📊 Defaulting {len(incorrect_answers)} incorrect answers to knowledge_gap")
					else:
						# No incorrect answers - all zeros is correct
						if current_app:
							current_app.logger.info("ℹ️ All answers correct - error_distribution is all zeros (expected)")
			except Exception as e:
				try:
					if current_app:
						current_app.logger.warning(f"⚠️ Failed to calculate error_distribution: {str(e)}")
					# Fallback: if calculation fails, default all incorrect answers to knowledge_gap
					incorrect_answers = [q for q in questions_list if not q.get("is_correct", False)]
					if incorrect_answers:
						validated_dist["knowledge_gap"] = len(incorrect_answers)
						if current_app:
							current_app.logger.info(f"📊 Fallback: Defaulting {len(incorrect_answers)} incorrect answers to knowledge_gap")
				except:
					pass
		
		# Ensure all error types are present (even if 0) - required for frontend graph
		for error_type in VALID_ERROR_TYPES:
			if error_type not in validated_dist:
				validated_dist[error_type] = 0
		
		rca["error_distribution"] = validated_dist
		
		# Fix primary_weakness to match the highest value in error_distribution
		# This ensures consistency between the pie chart and the primary weakness display
		if any(validated_dist.values()):
			# Find the error type with the highest count
			primary_weakness = max(validated_dist.items(), key=lambda x: x[1])[0]
		else:
			# If all values are 0, default to knowledge_gap
			primary_weakness = "knowledge_gap"
		
		# Validate the calculated primary_weakness
		try:
			rca["primary_weakness"] = validate_error_type(primary_weakness)
		except ValueError:
			# If validation fails, use knowledge_gap as fallback
			rca["primary_weakness"] = "knowledge_gap"
		
		# Log if AI's primary_weakness didn't match the calculated one (for debugging)
		ai_primary_weakness = rca.get("primary_weakness")
		if ai_primary_weakness and ai_primary_weakness != primary_weakness:
			import logging
			logging.warning(
				f"AI returned primary_weakness '{ai_primary_weakness}' but error_distribution shows "
				f"'{primary_weakness}' as highest. Using calculated value for consistency."
			)
		
		# Validate analysis_summary (ensure it's in second person)
		if "analysis_summary" not in result:
			# Generate a default summary if missing (in second person)
			overall_accuracy = overall_perf.get("accuracy", 0)
			weak_topics = [t for t in result["topic_breakdown"] if t.get("status") == "weak"]
			primary_weakness = rca.get("primary_weakness", "knowledge_gap")
			
			summary_parts = []
			if overall_accuracy < 60:
				summary_parts.append(f"Your performance shows significant gaps with {overall_accuracy:.1f}% accuracy.")
			elif overall_accuracy < 75:
				summary_parts.append(f"Your performance is developing with {overall_accuracy:.1f}% accuracy.")
			else:
				summary_parts.append(f"You demonstrated strong performance with {overall_accuracy:.1f}% accuracy.")
			
			if weak_topics:
				summary_parts.append(f"You have {len(weak_topics)} weak topic(s) requiring focused attention.")
			
			weakness_names = {
				"conceptual_gap": "conceptual understanding",
				"procedural_error": "procedural application",
				"careless_mistake": "attention to detail",
				"knowledge_gap": "foundational knowledge",
				"misinterpretation": "question interpretation"
			}
			weakness_name = weakness_names.get(primary_weakness, primary_weakness)
			summary_parts.append(f"Your primary weakness is in {weakness_name}.")
			
			result["analysis_summary"] = " ".join(summary_parts) if summary_parts else f"Your diagnostic analysis shows an overall accuracy of {overall_accuracy:.1f}%."
		else:
			# Ensure analysis_summary is a string
			if not isinstance(result["analysis_summary"], str):
				result["analysis_summary"] = str(result["analysis_summary"])
			# Ensure it's not empty
			if not result["analysis_summary"].strip():
				overall_accuracy = overall_perf.get("accuracy", 0)
				result["analysis_summary"] = f"Your diagnostic analysis shows an overall accuracy of {overall_accuracy:.1f}%."
			# Check if it needs to be converted from third person to second person
			# Common patterns: "The student" -> "You", "Student's" -> "Your", "Student" -> "You"
			summary = result["analysis_summary"]
			# Simple conversion for common patterns (if AI didn't follow instructions)
			if "the student" in summary.lower() or "student's" in summary.lower():
				# Log warning but don't auto-convert (let AI fix it in next generation)
				try:
					if current_app:
						current_app.logger.warning("AI returned analysis_summary in third person. It should be in second person ('You/Your').")
				except:
					pass
		
		# Fix Issue 3: Validate and correct predicted_jamb_score
		# This ensures score is 0-400 and confidence_interval is not "N/A"
		if "predicted_jamb_score" not in result:
			raise ValueError("Missing 'predicted_jamb_score' in AI response")
		
		result["predicted_jamb_score"] = validate_and_correct_jamb_score(
			result["predicted_jamb_score"],
			overall_accuracy
		)
		
		# Validate study_plan
		if "study_plan" not in result:
			raise ValueError("Missing 'study_plan' in AI response")
		
		study_plan = result["study_plan"]
		if "weekly_schedule" not in study_plan:
			raise ValueError("Missing 'weekly_schedule' in study_plan")
		
		weekly_schedule = study_plan["weekly_schedule"]
		if len(weekly_schedule) != 6:
			raise ValueError(f"Study plan must have exactly 6 weeks, got {len(weekly_schedule)}")
		
		# Validate recommendations
		if "recommendations" not in result:
			result["recommendations"] = []
		
		return result

