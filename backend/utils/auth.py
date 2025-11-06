"""
Authentication utilities for Supabase Auth JWT validation
"""
import os
import jwt
import requests
from typing import Optional
from functools import wraps
from flask import request, jsonify, current_app


class SupabaseAuth:
	"""Helper class for Supabase Auth JWT validation"""
	
	def __init__(self, supabase_url: str, supabase_anon_key: str):
		self.supabase_url = supabase_url
		self.supabase_anon_key = supabase_anon_key
		self.jwks_cache = None
		self.jwks_cache_time = None
	
	def get_jwks(self):
		"""Fetch Supabase JWKS (JSON Web Key Set) for token verification"""
		# Cache JWKS for 1 hour
		import time
		if self.jwks_cache and self.jwks_cache_time and (time.time() - self.jwks_cache_time) < 3600:
			return self.jwks_cache
		
		try:
			jwks_url = f"{self.supabase_url}/.well-known/jwks.json"
			response = requests.get(jwks_url, timeout=5)
			response.raise_for_status()
			self.jwks_cache = response.json()
			self.jwks_cache_time = time.time()
			return self.jwks_cache
		except Exception:
			# Fallback: return None, will use simple validation
			return None
	
	def verify_token(self, token: str) -> Optional[dict]:
		"""
		Verify Supabase JWT token and return payload
		Returns None if token is invalid
		"""
		if not token:
			return None
		
		# Remove "Bearer " prefix if present
		if token.startswith("Bearer "):
			token = token[7:]
		
		try:
			# Decode without verification first to get header
			unverified = jwt.decode(token, options={"verify_signature": False})
			
			# Try JWKS verification first (most secure)
			try:
				from jwt import PyJWKClient
				jwks_url = f"{self.supabase_url}/.well-known/jwks.json"
				jwks_client = PyJWKClient(jwks_url)
				signing_key = jwks_client.get_signing_key_from_jwt(token)
				payload = jwt.decode(token, signing_key.key, algorithms=["RS256"])
			except (ImportError, Exception):
				# Fallback: try HS256 with anon key
				try:
					payload = jwt.decode(token, self.supabase_anon_key, algorithms=["HS256"])
				except:
					# Last resort: in debug mode, return unverified (development only)
					if current_app and current_app.config.get("DEBUG"):
						payload = unverified
					else:
						return None
			
			# Extract user ID from payload
			user_id = payload.get("sub") or payload.get("user_id")
			if not user_id:
				return None
			
			return {
				"user_id": user_id,
				"email": payload.get("email"),
				"payload": payload
			}
		except jwt.ExpiredSignatureError:
			return None
		except jwt.InvalidTokenError:
			return None
		except Exception:
			return None


def get_auth() -> Optional[SupabaseAuth]:
	"""Get SupabaseAuth instance from app context"""
	try:
		if current_app:
			auth = current_app.extensions.get("supabase_auth")
			if auth:
				return auth
			# Create if not exists
			supabase_url = current_app.config.get("SUPABASE_URL")
			supabase_key = current_app.config.get("SUPABASE_ANON_KEY")
			if supabase_url and supabase_key:
				auth = SupabaseAuth(supabase_url, supabase_key)
				current_app.extensions["supabase_auth"] = auth
				return auth
	except (RuntimeError, AttributeError):
		pass
	return None


def get_current_user_id() -> Optional[str]:
	"""
	Extract current user ID from Authorization header
	Returns None if not authenticated
	"""
	auth_header = request.headers.get("Authorization")
	if not auth_header:
		return None
	
	auth = get_auth()
	if not auth:
		return None
	
	user_info = auth.verify_token(auth_header)
	if user_info:
		return user_info["user_id"]
	return None


def require_auth(f):
	"""
	Decorator to require authentication for a route
	Returns 401 if not authenticated
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		user_id = get_current_user_id()
		if not user_id:
			return jsonify({"error": "unauthorized", "message": "Authentication required"}), 401
		# Add user_id to kwargs for route to use
		kwargs["current_user_id"] = user_id
		return f(*args, **kwargs)
	return decorated_function


def optional_auth(f):
	"""
	Decorator for routes that work with or without auth
	Adds current_user_id to kwargs if authenticated, None otherwise
	"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		user_id = get_current_user_id()
		kwargs["current_user_id"] = user_id
		return f(*args, **kwargs)
	return decorated_function

