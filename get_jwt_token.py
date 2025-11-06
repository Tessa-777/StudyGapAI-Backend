"""
Get JWT Token from Supabase for Testing

This script helps you get a JWT token from Supabase Auth for testing backend endpoints.
You can use either:
1. Email/Password signup/signin (easiest for testing)
2. Google OAuth (requires manual browser flow)
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
    sys.exit(1)

# Remove trailing slash
SUPABASE_URL = SUPABASE_URL.rstrip("/")


def sign_up_with_email(email: str, password: str, name: str = "Test User"):
    """Sign up a new user with email/password"""
    url = f"{SUPABASE_URL}/auth/v1/signup"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "password": password,
        "data": {"name": name}
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code in [200, 201]:
        result = response.json()
        return result.get("access_token"), result.get("user")
    else:
        print(f"Sign up failed: {response.status_code}")
        print(response.text)
        return None, None


def sign_up_with_supabase_client(email: str, password: str, name: str = "Test User"):
    """Sign up using Supabase Python client"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"name": name}
            }
        })
        if response.user and response.session:
            return response.session.access_token, response.user
    except Exception as e:
        print(f"Supabase client signup failed: {e}")
    return None, None


def sign_in_with_supabase_client(email: str, password: str):
    """Sign in using Supabase Python client"""
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        if response.user and response.session:
            return response.session.access_token, response.user
    except Exception as e:
        print(f"Supabase client signin failed: {e}")
    return None, None


def create_user_via_admin(email: str, password: str, name: str = "Test User"):
    """Create user via Admin API (requires service role key)"""
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not service_role_key:
        return None, None
    
    url = f"{SUPABASE_URL}/auth/v1/admin/users"
    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "password": password,
        "user_metadata": {"name": name},
        "email_confirm": True  # Auto-confirm email
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code in [200, 201]:
        # Now sign in to get token
        token, user = sign_in_with_email(email, password)
        return token, user
    else:
        print(f"Admin API signup failed: {response.status_code}")
        print(response.text)
        return None, None


def sign_in_with_email(email: str, password: str):
    """Sign in with email/password"""
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result.get("access_token"), result.get("user")
    else:
        print(f"Sign in failed: {response.status_code}")
        print(response.text)
        return None, None


def get_token_from_existing_user():
    """Try to get token from existing user or create one"""
    # Try different email formats
    test_emails = [
        "test@studygapai.com",
        "testuser@example.com",
        f"test{os.urandom(4).hex()}@example.com"  # Random email
    ]
    test_password = "TestPassword123!"
    
    for test_email in test_emails:
        print(f"\nAttempting to sign in with email: {test_email}")
        
        # Try Supabase client first (more reliable)
        token, user = sign_in_with_supabase_client(test_email, test_password)
        if token:
            break
        
        # Try REST API
        token, user = sign_in_with_email(test_email, test_password)
        if token:
            break
        
        print(f"Sign in failed. Trying to create new user...")
        
        # Try Supabase client signup
        token, user = sign_up_with_supabase_client(test_email, test_password)
        if token:
            break
        
        # Try REST API signup
        token, user = sign_up_with_email(test_email, test_password)
        if token:
            break
        
        # Try admin API if available
        print(f"Trying admin API method...")
        token, user = create_user_via_admin(test_email, test_password)
        if token:
            break
    
    if token and user:
        print("\n" + "="*60)
        print("SUCCESS! JWT Token obtained:")
        print("="*60)
        print(f"\nToken: {token}\n")
        print(f"User ID: {user.get('id')}")
        print(f"Email: {user.get('email')}")
        print("\n" + "="*60)
        print("\nSave this token to use in API tests:")
        print(f"export JWT_TOKEN='{token}'")
        print("\nOr use it directly in the test script.")
        print("="*60)
        
        # Save to file for easy access
        with open(".test_token", "w") as f:
            f.write(token)
        print("\nToken saved to .test_token file")
        
        return token, user
    else:
        print("\nERROR: Could not obtain JWT token")
        print("\nAlternative: Get token manually from Supabase Dashboard:")
        print("1. Go to Supabase Dashboard → Authentication → Users")
        print("2. Create a user or use existing one")
        print("3. Copy the user's UUID")
        print("4. Use Supabase Admin API or generate token via Auth API")
        return None, None


if __name__ == "__main__":
    print("="*60)
    print("Supabase JWT Token Generator for Testing")
    print("="*60)
    print(f"\nSupabase URL: {SUPABASE_URL}")
    print(f"Anon Key: {SUPABASE_ANON_KEY[:20]}...")
    print("\n" + "-"*60)
    
    token, user = get_token_from_existing_user()
    
    if token:
        print("\n✅ Ready to test! Run test_all_endpoints.py next.")
    else:
        print("\n❌ Failed to get token. Check your Supabase configuration.")
        sys.exit(1)

