# Testing Backend with JWT Authentication

This guide shows you how to get a JWT token from Supabase and test all backend endpoints.

## Prerequisites

1. ✅ Supabase project set up
2. ✅ Google OAuth configured in Supabase Dashboard
3. ✅ Backend running (locally or on Railway)
4. ✅ `.env` file configured with Supabase credentials

## Step 1: Get JWT Token

### Method 1: Automated Script (Recommended)

Run the token generator script:

```bash
python get_jwt_token.py
```

This script will:
- Try to sign in with a test email
- If user doesn't exist, create a new user
- Save the JWT token to `.test_token` file
- Display the token for manual use

**Note**: The script uses email/password authentication for testing. In production, your frontend will use Google OAuth.

### Method 2: Manual Token via Supabase Dashboard

If the script doesn't work, create a user manually:

1. **Go to Supabase Dashboard** → Authentication → Users
2. **Click "Add User"** → "Create new user"
3. **Fill in**:
   - Email: `test@example.com` (or any valid email)
   - Password: `TestPassword123!`
   - Auto Confirm User: ✅ (check this)
4. **Click "Create User"**
5. **Copy the User UUID** from the user list

Then use this Python script to get the token:

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Sign in
response = supabase.auth.sign_in_with_password({
    "email": "test@example.com",  # Use the email you created
    "password": "TestPassword123!"
})

token = response.session.access_token
print(f"Token: {token}")

# Save to file
with open(".test_token", "w") as f:
    f.write(token)
```

### Method 3: Using Supabase REST API

```bash
curl -X POST 'https://YOUR_PROJECT.supabase.co/auth/v1/token?grant_type=password' \
  -H "apikey: YOUR_ANON_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'
```

Extract the `access_token` from the response.

## Step 2: Test All Endpoints

Run the comprehensive test suite:

```bash
python test_all_endpoints.py
```

This will test:
- ✅ Public endpoints (health, questions, explain-answer, analytics)
- ✅ Authenticated endpoints (user profile, quiz, AI analysis, study plans, progress)
- ✅ Security (unauthorized access rejection)

## Step 3: Test Individual Endpoints

You can test endpoints manually using curl:

```bash
# Set your token (from .test_token file or manual)
export JWT_TOKEN="your-token-here"

# Test authenticated endpoint
curl -X GET http://localhost:5000/api/users/me \
  -H "Authorization: Bearer $JWT_TOKEN"

# Test public endpoint
curl http://localhost:5000/health
```

## Testing on Railway

If your backend is deployed on Railway:

1. Update `BACKEND_URL` in `.env`:
   ```
   BACKEND_URL=https://your-app.railway.app
   ```

2. Run the test scripts:
   ```bash
   python get_jwt_token.py
   python test_all_endpoints.py
   ```

## Troubleshooting

### "401 Unauthorized" errors
- Check that your JWT token is valid
- Verify Supabase Auth is properly configured
- Ensure RLS policies are set up correctly
- Token might be expired (run `get_jwt_token.py` again)

### "403 Forbidden" errors
- Verify the user owns the resource (quiz, study plan, etc.)
- Check RLS policies allow the operation
- Ensure user_id matches in JWT and database

### Email/Password Auth Not Working
- Check if Email auth is enabled in Supabase Dashboard → Authentication → Providers
- Try creating user manually via Dashboard first
- Use Method 2 (Manual Token) above

### Token expired
- Tokens expire after 1 hour by default
- Run `get_jwt_token.py` again to get a new token

### Database connection errors
- Verify `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`
- Check Supabase project is active
- Verify RLS policies allow operations

## Expected Test Results

All tests should pass:
- ✅ Health Check: 200 OK
- ✅ Get Questions: 200 OK (returns questions)
- ✅ Get Current User: 200 OK (returns user profile)
- ✅ Update Target Score: 200 OK
- ✅ Start Quiz: 201 Created (returns quiz ID)
- ✅ Submit Quiz: 200 OK
- ✅ Get Quiz Results: 200 OK
- ✅ Analyze Diagnostic: 200 OK (returns analysis)
- ✅ Generate Study Plan: 201 Created
- ✅ Get Progress: 200 OK
- ✅ Mark Progress Complete: 201 Created
- ✅ Unauthorized Access: 401 Unauthorized

## Next Steps

After successful testing:
1. ✅ Backend is ready for frontend integration
2. ✅ Frontend can use Supabase Auth SDK to get tokens
3. ✅ All endpoints are secured and working
4. ✅ RLS policies are protecting data

