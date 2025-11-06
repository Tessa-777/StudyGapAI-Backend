# Quick Start: Get JWT Token and Test Backend

## Step 1: Create a Test User in Supabase Dashboard

1. Go to **Supabase Dashboard** → **Authentication** → **Users**
2. Click **"Add User"** → **"Create new user"**
3. Fill in:
   - **Email**: `test@example.com` (or any valid email)
   - **Password**: `TestPassword123!` (or any password)
   - ✅ **Auto Confirm User** (IMPORTANT: check this!)
4. Click **"Create User"**

## Step 2: Get JWT Token

Run the manual token script:

```bash
python get_jwt_token_manual.py
```

Enter the email and password you just created. The script will:
- Sign in to Supabase
- Get the JWT token
- Save it to `.test_token` file

## Step 3: Test All Endpoints

Run the comprehensive test suite:

```bash
python test_all_endpoints.py
```

This will test all endpoints with your JWT token.

---

## Alternative: Use Supabase Python Client Directly

If you prefer, you can get the token directly:

```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)

# Sign in with the user you created
response = supabase.auth.sign_in_with_password({
    "email": "test@example.com",  # Your test email
    "password": "TestPassword123!"  # Your test password
})

token = response.session.access_token
print(f"Token: {token}")

# Save to file
with open(".test_token", "w") as f:
    f.write(token)
```

Then run:
```bash
python test_all_endpoints.py
```

---

## Troubleshooting

### "Email address is invalid"
- Make sure Email auth is enabled in Supabase Dashboard → Authentication → Providers
- Try a different email format (e.g., `testuser@gmail.com`)

### "Invalid login credentials"
- Verify the email and password are correct
- Make sure you checked "Auto Confirm User" when creating the user
- Try creating a new user

### "401 Unauthorized" in tests
- Check that `.test_token` file exists and contains a valid token
- Token might be expired (get a new one)
- Verify Supabase Auth is properly configured

---

## Expected Results

After running `test_all_endpoints.py`, you should see:
- ✅ All public endpoints working
- ✅ All authenticated endpoints working
- ✅ Security tests passing (401 for unauthorized access)

If all tests pass, your backend is ready! 🎉

