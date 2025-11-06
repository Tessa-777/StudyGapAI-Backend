import os


class AppConfig:
	ENV = os.getenv("FLASK_ENV", "production")
	DEBUG = ENV != "production"
	TESTING = os.getenv("TESTING", "false").lower() == "true"
	SECRET_KEY = os.getenv("SECRET_KEY", "insecure-dev-secret")

	# Supabase
	SUPABASE_URL = os.getenv("SUPABASE_URL")
	SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
	USE_IN_MEMORY_DB = os.getenv("USE_IN_MEMORY_DB", "true").lower() == "true"

	# AI
	GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
	AI_MODEL_NAME = os.getenv("AI_MODEL_NAME", "gemini-2.5-flash")
	AI_MOCK = os.getenv("AI_MOCK", "true").lower() == "true"

	# App
	APP_NAME = os.getenv("APP_NAME", "StudyGapAI Backend")
	APP_VERSION = os.getenv("APP_VERSION", "0.1.0")


