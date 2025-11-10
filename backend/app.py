import os
import logging
from flask import Flask, jsonify
from dotenv import load_dotenv

from .config import AppConfig
from .routes.users import users_bp
from .routes.quiz import quiz_bp
from .routes.ai import ai_bp
from .routes.progress import progress_bp
from .routes.analytics import analytics_bp
from .routes.resources import resources_bp
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

# Configure logging to show in terminal/console
logging.basicConfig(
	level=logging.INFO,  # Set to INFO to show info, warning, and error logs
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
	datefmt='%Y-%m-%d %H:%M:%S'
)

# Get Flask's logger and set level
flask_logger = logging.getLogger('flask')
flask_logger.setLevel(logging.INFO)

# Also configure werkzeug (Flask's WSGI server) logger
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.INFO)


def create_app() -> Flask:
	app = Flask(__name__)
	app.config.from_object(AppConfig)
	
	# Configure app logger to show logs in terminal
	# Flask's default logger level might be WARNING, so we set it to INFO
	# Always show INFO level in development, WARNING in production
	is_debug = app.config.get("DEBUG", False)
	
	# Set logger level based on debug mode
	app.logger.setLevel(logging.DEBUG if is_debug else logging.INFO)
	
	# Remove existing handlers to avoid duplicate logs
	app.logger.handlers = []
	
	# Create console handler
	console_handler = logging.StreamHandler()
	console_handler.setLevel(logging.DEBUG if is_debug else logging.INFO)
	
	# Create formatter with timestamp and level
	formatter = logging.Formatter(
		'%(asctime)s [%(levelname)s] %(name)s: %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S'
	)
	console_handler.setFormatter(formatter)
	
	# Add handler to app logger
	app.logger.addHandler(console_handler)
	
	# Also configure root logger to ensure all logs are shown
	root_logger = logging.getLogger()
	root_logger.setLevel(logging.DEBUG if is_debug else logging.INFO)
	if not root_logger.handlers:
		root_logger.addHandler(console_handler)
	
	app.logger.info("=" * 60)
	app.logger.info("Flask app logger configured - logs will appear in terminal")
	app.logger.info(f"Debug mode: {is_debug}, Log level: {'DEBUG' if is_debug else 'INFO'}")
	app.logger.info("=" * 60)
	
	# Enhanced CORS configuration
	# Get CORS origins from environment, default to localhost for development
	cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:5173")
	
	# Support comma-separated origins, or "*" for all origins
	if cors_origins_env == "*":
		origins_list = "*"
	else:
		# Split by comma and strip whitespace from each origin
		origins_list = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
	
	# Log CORS configuration for debugging (only in development)
	if app.config.get("DEBUG"):
		app.logger.info(f"CORS configured for origins: {origins_list}")
	
	# CORS configuration - allow all routes
	# This allows requests from the specified origins
	CORS(app, 
		 resources={r"/*": {
			 "origins": origins_list,
			 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
			 "allow_headers": ["Content-Type", "Authorization"],
			 "supports_credentials": True,
			 "expose_headers": ["Content-Type", "Authorization"]
		 }}
	)

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
	
	# Use service role key for database operations (bypasses RLS)
	# Fall back to anon key if service role key not available
	supabase_db_key = (
		app.config.get("SUPABASE_SERVICE_ROLE_KEY") or 
		app.config.get("SUPABASE_ANON_KEY") or 
		""
	).strip()
	
	# Anon key is still needed for JWT validation (SupabaseAuth)
	supabase_anon_key = (app.config.get("SUPABASE_ANON_KEY") or "").strip()
	
	# Debug logging (only in development)
	if app.config.get("DEBUG"):
		print(f"[DEBUG] USE_IN_MEMORY_DB: {use_in_memory}")
		print(f"[DEBUG] SUPABASE_URL: {supabase_url[:50] if supabase_url else 'NOT SET'}...")
		print(f"[DEBUG] SUPABASE_DB_KEY: {'SERVICE_ROLE' if app.config.get('SUPABASE_SERVICE_ROLE_KEY') else 'ANON' if supabase_db_key else 'NOT SET'}")
		print(f"[DEBUG] SUPABASE_ANON_KEY: {'SET' if supabase_anon_key else 'NOT SET'} (for JWT validation)")
	
	if use_in_memory or not (supabase_url and supabase_db_key):
		from .repositories.memory_repository import InMemoryRepository
		app.extensions["repository"] = InMemoryRepository()
		if not use_in_memory:
			import warnings
			warnings.warn("USE_IN_MEMORY_DB=false but Supabase credentials missing/invalid. Using in-memory repository.")
	else:
		from .repositories.supabase_repository import SupabaseRepository
		try:
			# Use service role key (or anon key as fallback) for database operations
			app.extensions["repository"] = SupabaseRepository(supabase_url, supabase_db_key)
			if app.config.get("DEBUG"):
				key_type = "SERVICE_ROLE" if app.config.get("SUPABASE_SERVICE_ROLE_KEY") else "ANON"
				print(f"[DEBUG] Supabase repository initialized successfully with {key_type} key")
		except Exception as e:
			import warnings
			warnings.warn(f"Failed to initialize Supabase repository: {e}. Falling back to in-memory repository.")
			print(f"[ERROR] Supabase initialization failed: {e}")
			print(f"[ERROR] URL used: {supabase_url}")
			from .repositories.memory_repository import InMemoryRepository
			app.extensions["repository"] = InMemoryRepository()

	# Initialize Supabase Auth helper for JWT validation (uses anon key, not service role)
	from .utils.auth import SupabaseAuth
	if supabase_url and supabase_anon_key:
		app.extensions["supabase_auth"] = SupabaseAuth(supabase_url, supabase_anon_key)
		if app.config.get("DEBUG"):
			print(f"[DEBUG] Supabase Auth initialized (for JWT validation)")

	# Root endpoint
	@app.get("/")
	def root() -> tuple:
		return jsonify({
			"message": "StudyGapAI Backend API",
			"status": "running",
			"version": os.getenv("APP_VERSION", "0.1.0"),
			"endpoints": {
				"health": "/health",
				"users": "/api/users",
				"quiz": "/api/quiz",
				"ai": "/api/ai",
				"progress": "/api/progress",
				"analytics": "/api/analytics",
				"resources": "/api/resources"
			}
		}), 200

	# Health endpoint
	@app.get("/health")
	def health() -> tuple:
		return jsonify({"status": "ok", "version": os.getenv("APP_VERSION", "0.1.0")}), 200

	# Register blueprints
	app.register_blueprint(users_bp, url_prefix="/api/users")
	app.register_blueprint(quiz_bp, url_prefix="/api/quiz")  # Changed from /api to /api/quiz
	app.register_blueprint(ai_bp, url_prefix="/api/ai")
	app.register_blueprint(progress_bp, url_prefix="/api")
	app.register_blueprint(analytics_bp, url_prefix="/api")
	app.register_blueprint(resources_bp, url_prefix="/api")

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


