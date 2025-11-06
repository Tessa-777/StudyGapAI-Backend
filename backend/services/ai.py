import os
import hashlib
import json
from typing import Any, Dict, List
from flask import current_app

try:
	from google import genai  # type: ignore
except Exception:  # pragma: no cover
	genai = None


class AIService:
	def __init__(self, api_key: str | None, model_name: str, mock: bool) -> None:
		self.mock = mock or not api_key or genai is None
		self.model_name = model_name
		self.client = None
		if not self.mock and api_key and genai is not None:
			# New API: genai.Client() automatically picks up GEMINI_API_KEY from env
			# But we can also pass api_key directly if provided
			if api_key:
				os.environ["GEMINI_API_KEY"] = api_key
			self.client = genai.Client(api_key=api_key)

	def _mock_analysis(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
		incorrect = [r for r in responses if not r.get("isCorrect")]
		projected = 165
		return {
			"weakTopics": [{"topicId": r.get("questionId"), "topicName": "Algebra", "severity": "medium", "rootCause": "factoring"} for r in incorrect[:3]],
			"strongTopics": [{"topicId": r.get("questionId"), "topicName": "Geometry", "score": 90} for r in responses[:3]],
			"analysisSummary": "Baseline mock analysis for testing.",
			"projectedScore": projected,
			"foundationalGaps": [{"gapDescription": "Weak arithmetic fluency", "affectedTopics": ["Algebra"]}],
		}

	def analyze_diagnostic(self, responses: List[Dict[str, Any]]) -> Dict[str, Any]:
		if self.mock:
			return self._mock_analysis(responses)

		# Caching by hash of responses
		cache = None
		try:
			if current_app:
				cache = current_app.extensions.get("cache_instance")
		except (RuntimeError, AttributeError):
			pass
		
		cache_key = None
		if cache:
			cache_key = f"ai:analyze:{hashlib.sha256(json.dumps(responses, sort_keys=True).encode()).hexdigest()}"
			cached = cache.get(cache_key)
			if cached:
				return cached

		prompt = (
			"You are an expert JAMB Mathematics tutor in Nigeria.\n\n"
			"A student just completed a 30-question diagnostic quiz. Analyze their performance and identify:\n"
			"1. Weak topics (topics where they scored <60%)\n"
			"2. Strong topics (topics where they scored >80%)\n"
			"3. ROOT CAUSES of weaknesses (e.g., 'struggles with quadratics because doesn't understand factoring')\n"
			"4. Foundational gaps (basic concepts they're missing)\n\n"
			f"Student data:\n{responses}\n\n"
			"CRITICAL: Return ONLY valid JSON, no explanations, no markdown, no code blocks. Start directly with {.\n"
			"Return a JSON object with this EXACT structure:\n"
			'{"weakTopics": [{"topicId": "...", "topicName": "...", "severity": "...", "rootCause": "..."}], '
			'"strongTopics": [{"topicId": "...", "topicName": "...", "score": 85}], '
			'"analysisSummary": "...", "projectedScore": 165, '
			'"foundationalGaps": [{"gapDescription": "...", "affectedTopics": ["..."]}]}'
		)
		# New API: client.models.generate_content()
		response = self.client.models.generate_content(
			model=self.model_name,
			contents=prompt
		)
		# Extract text from response - new API has .text attribute
		text = response.text if hasattr(response, "text") and response.text else None
		
		# Fallback: try to extract from candidates if .text is empty
		if not text and hasattr(response, 'candidates') and response.candidates:
			candidate = response.candidates[0]
			if hasattr(candidate, 'content') and candidate.content:
				if hasattr(candidate.content, 'parts') and candidate.content.parts:
					text = candidate.content.parts[0].text
		
		if not text:
			raise ValueError(f"Empty response from Gemini API. Response: {response}")
		
		# Clean text - remove markdown code blocks if present
		text = text.strip()
		if text.startswith('```json'):
			text = text[7:]
		if text.startswith('```'):
			text = text[3:]
		if text.endswith('```'):
			text = text[:-3]
		text = text.strip()
		
		try:
			result_json = json.loads(text)
		except json.JSONDecodeError as e:
			raise ValueError(f"Failed to parse JSON from Gemini response. Text: {text[:200]}... Error: {e}")
		
		if cache and cache_key:
			cache.set(cache_key, result_json, timeout=300)
		return result_json

	def generate_study_plan(self, weak_topics: List[Dict[str, Any]], target_score: int, current_score: int, weeks_available: int = 6) -> Dict[str, Any]:
		if self.mock:
			weeks = []
			for i in range(weeks_available):
				weeks.append({
					"weekNumber": i + 1,
					"focus": "Foundations first" if i == 0 else "Progressive mastery",
					"topics": [
						{"topicId": "algebra", "topicName": "Algebra", "dailyGoals": "Practice 10 problems", "estimatedTime": "40 mins/day",
						 "resources": [{"type": "video", "title": "Algebra Basics", "url": "https://example.com", "duration": 15}]},
					],
					"milestones": "Complete 50 practice problems" if i == 0 else "Take mini-quiz",
					"daily": [{"day": d + 1, "minutes": 40} for d in range(7)],
				})
			return {"weeks": weeks}

		# Cache by weak topics + params
		cache = None
		try:
			if current_app:
				cache = current_app.extensions.get("cache_instance")
		except (RuntimeError, AttributeError):
			pass
		
		cache_key = None
		if cache:
			cache_key = f"ai:plan:{hashlib.sha256(json.dumps({"w": weak_topics, "t": target_score, "c": current_score, "n": weeks_available}, sort_keys=True).encode()).hexdigest()}"
			cached = cache.get(cache_key)
			if cached:
				return cached

		prompt = (
			"You are a JAMB prep expert. Create a 6-week study plan for a student with these weak topics: "
			f"{weak_topics}\n\nTarget score: {target_score}\nCurrent projected score: {current_score}\nWeeks available: {weeks_available}\n\n"
			"Rules:\n- Start with foundational gaps FIRST\n- Build progressively (don't jump to advanced topics)\n- Each week should have 3-4 topics max\n- Include daily time estimates (30-45 mins/day)\n- Prioritize topics with highest JAMB weight\n\n"
			"CRITICAL: Return ONLY valid JSON, no explanations, no markdown, no code blocks. Start directly with {.\n"
			"Return JSON structured as N weeks of daily study goals with fields weekNumber, focus, topics[{topicId, topicName, dailyGoals, estimatedTime, resources[{type, title, url, duration}]}], milestones, daily[{day, minutes}]."
		)
		# New API: client.models.generate_content()
		response = self.client.models.generate_content(
			model=self.model_name,
			contents=prompt
		)
		# Extract text from response - new API has .text attribute
		text = response.text if hasattr(response, "text") and response.text else None
		
		# Fallback: try to extract from candidates if .text is empty
		if not text and hasattr(response, 'candidates') and response.candidates:
			candidate = response.candidates[0]
			if hasattr(candidate, 'content') and candidate.content:
				if hasattr(candidate.content, 'parts') and candidate.content.parts:
					text = candidate.content.parts[0].text
		
		if not text:
			raise ValueError(f"Empty response from Gemini API. Response: {response}")
		
		# Clean text - remove markdown code blocks if present
		text = text.strip()
		if text.startswith('```json'):
			text = text[7:]
		if text.startswith('```'):
			text = text[3:]
		if text.endswith('```'):
			text = text[:-3]
		text = text.strip()
		
		try:
			result_json = json.loads(text)
		except json.JSONDecodeError as e:
			raise ValueError(f"Failed to parse JSON from Gemini response. Text: {text[:200]}... Error: {e}")
		
		if cache and cache_key:
			cache.set(cache_key, result_json, timeout=300)
		return result_json

	def explain_answer(self, payload: Dict[str, Any]) -> Dict[str, Any]:
		if self.mock:
			return {
				"explanation": "Review the concept and try similar problems.",
				"correctReasoning": "Compare options, compute directly.",
				"commonMistake": "Mis-reading the question.",
				"relatedTopics": ["Algebra"],
			}

		prompt = (
			"Provide a concise explanation and correction for the following question/answer pair.\n"
			f"Data: {payload}\n\n"
			"CRITICAL: Return ONLY valid JSON, no explanations, no markdown, no code blocks. Start directly with {.\n"
			"Return JSON with keys: explanation, correctReasoning, commonMistake, relatedTopics."
		)
		# New API: client.models.generate_content()
		response = self.client.models.generate_content(
			model=self.model_name,
			contents=prompt
		)
		# Extract text from response - new API has .text attribute
		text = response.text if hasattr(response, "text") and response.text else None
		
		# Fallback: try to extract from candidates if .text is empty
		if not text and hasattr(response, 'candidates') and response.candidates:
			candidate = response.candidates[0]
			if hasattr(candidate, 'content') and candidate.content:
				if hasattr(candidate.content, 'parts') and candidate.content.parts:
					text = candidate.content.parts[0].text
		
		if not text:
			raise ValueError(f"Empty response from Gemini API. Response: {response}")
		
		# Clean text - remove markdown code blocks if present
		text = text.strip()
		if text.startswith('```json'):
			text = text[7:]
		if text.startswith('```'):
			text = text[3:]
		if text.endswith('```'):
			text = text[:-3]
		text = text.strip()
		
		try:
			return json.loads(text)
		except json.JSONDecodeError as e:
			raise ValueError(f"Failed to parse JSON from Gemini response. Text: {text[:200]}... Error: {e}")


