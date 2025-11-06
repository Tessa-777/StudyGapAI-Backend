"""
Get JWT Token - Manual Input Version

Use this if automated signup doesn't work.
First create a user manually in Supabase Dashboard, then run this script.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    print("ERROR: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
    sys.exit(1)

print("="*60)
print("Manual JWT Token Generator")
print("="*60)
print("\nFirst, create a user in Supabase Dashboard:")
print("1. Go to Supabase Dashboard → Authentication → Users")
print("2. Click 'Add User' → 'Create new user'")
print("3. Enter email and password")
print("4. Check 'Auto Confirm User'")
print("5. Click 'Create User'")
print("\n" + "-"*60)

email = input("\nEnter the email you created: ").strip()
password = input("Enter the password: ").strip()

if not email or not password:
    print("ERROR: Email and password are required")
    sys.exit(1)

try:
    supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    print("\nSigning in...")
    response = supabase.auth.sign_in_with_password({
        "email": email,
        "password": password
    })
    
    if response.user and response.session:
        token = response.session.access_token
        user_id = response.user.id
        
        print("\n" + "="*60)
        print("SUCCESS! JWT Token obtained:")
        print("="*60)
        print(f"\nToken: {token}\n")
        print(f"User ID: {user_id}")
        print(f"Email: {email}")
        print("\n" + "="*60)
        
        # Save to file
        with open(".test_token", "w") as f:
            f.write(token)
        print("\nToken saved to .test_token file")
        print("✅ Ready to test! Run test_all_endpoints.py next.")
        print("="*60)
    else:
        print("ERROR: Could not get token from response")
        sys.exit(1)
        
except Exception as e:
    print(f"\nERROR: Failed to sign in: {e}")
    print("\nTroubleshooting:")
    print("1. Verify email/password are correct")
    print("2. Check if Email auth is enabled in Supabase Dashboard")
    print("3. Ensure user is confirmed (check 'Auto Confirm User' when creating)")
    sys.exit(1)

