import os
from flask import Flask, jsonify
from dotenv import load_dotenv

from .config import AppConfig
from .routes.users import users_bp
from .routes.quiz import quiz_bp
from .routes.ai import ai_bp
from .routes.progress import progress_bp
from .routes.analytics import analytics_bp
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(AppConfig)
	CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ORIGINS", "*")}})

	# Cache setup (simple in-memory)
	from flask_caching import Cache
	app.config["CACHE_TYPE"] = "SimpleCache"
	app.config["CACHE_DEFAULT_TIMEOUT"] = 60
	cache = Cache()
	cache.init_app(app)
	# Flask-Caching stores itself in app.extensions["cache"][cache_instance]
	# We need to access it via the cache instance methods directly
	app.extensions["cache_instance"] = cache

	# Initialize repository singleton for in-memory mode
	# Store it on app instance so it persists across requests
	use_in_memory = app.config.get("USE_IN_MEMORY_DB", True)
	supabase_url = (app.config.get("SUPABASE_URL") or "").strip()
	supabase_key = (app.config.get("SUPABASE_ANON_KEY") or "").strip()
	
	# Debug logging (only in development)
	if app.config.get("DEBUG"):
		print(f"[DEBUG] USE_IN_MEMORY_DB: {use_in_memory}")
		print(f"[DEBUG] SUPABASE_URL: {supabase_url[:50] if supabase_url else 'NOT SET'}...")
		print(f"[DEBUG] SUPABASE_ANON_KEY: {'SET' if supabase_key else 'NOT SET'}")
	
	if use_in_memory or not (supabase_url and supabase_key):
		from .repositories.memory_repository import InMemoryRepository
		app.extensions["repository"] = InMemoryRepository()
		if not use_in_memory:
			import warnings
			warnings.warn("USE_IN_MEMORY_DB=false but Supabase credentials missing/invalid. Using in-memory repository.")
	else:
		from .repositories.supabase_repository import SupabaseRepository
		try:
			app.extensions["repository"] = SupabaseRepository(supabase_url, supabase_key)
			if app.config.get("DEBUG"):
				print(f"[DEBUG] Supabase repository initialized successfully")
		except Exception as e:
			import warnings
			warnings.warn(f"Failed to initialize Supabase repository: {e}. Falling back to in-memory repository.")
			print(f"[ERROR] Supabase initialization failed: {e}")
			print(f"[ERROR] URL used: {supabase_url}")
			from .repositories.memory_repository import InMemoryRepository
			app.extensions["repository"] = InMemoryRepository()

	# Initialize Supabase Auth helper for JWT validation
	from .utils.auth import SupabaseAuth
	if supabase_url and supabase_key:
		app.extensions["supabase_auth"] = SupabaseAuth(supabase_url, supabase_key)
		if app.config.get("DEBUG"):
			print(f"[DEBUG] Supabase Auth initialized")

	# Health endpoint
	@app.get("/health")
	def health() -> tuple:
		return jsonify({"status": "ok", "version": os.getenv("APP_VERSION", "0.1.0")}), 200

	# Register blueprints
	app.register_blueprint(users_bp, url_prefix="/api/users")
	app.register_blueprint(quiz_bp, url_prefix="/api")
	app.register_blueprint(ai_bp, url_prefix="/api/ai")
	app.register_blueprint(progress_bp, url_prefix="/api")
	app.register_blueprint(analytics_bp, url_prefix="/api")

	# Error handlers
	@app.errorhandler(400)
	def bad_request(error):
		return jsonify({"error": "bad_request", "message": str(error)}), 400

	@app.errorhandler(404)
	def not_found(error):
		return jsonify({"error": "not_found", "message": "Resource not found"}), 404

	@app.errorhandler(500)
	def server_error(error):
		return jsonify({"error": "server_error", "message": "An unexpected error occurred"}), 500

	return app


app = create_app()


