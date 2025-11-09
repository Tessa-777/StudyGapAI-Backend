# StudyGapAI Backend API

Flask backend API for StudyGapAI - JAMB diagnostic platform.

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (create `.env` file):
```bash
FLASK_ENV=development
SECRET_KEY=your-secret-key
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
USE_IN_MEMORY_DB=false
GOOGLE_API_KEY=your-google-api-key
AI_MODEL_NAME=gemini-1.5-flash
AI_MOCK=false
CORS_ORIGINS=http://localhost:5173
```

3. Run the server:
```bash
python main.py
```

Or use the development script:
```bash
python scripts/run_flask.py
```

## Replit Deployment

### Setup on Replit

1. **Import Repository**
   - Go to Replit and create a new Repl
   - Import from GitHub repository
   - Select Python as the language

2. **Install Dependencies**
   - Replit will automatically install from `requirements.txt`
   - Or run: `pip install -r requirements.txt`

3. **Set Environment Variables (Secrets)**
   - Go to Secrets tab (lock icon) in Replit
   - Add the following secrets:
     - `FLASK_ENV` = `production`
     - `SECRET_KEY` = (generate a secure random string)
     - `SUPABASE_URL` = (your Supabase project URL)
     - `SUPABASE_ANON_KEY` = (your Supabase anon key)
     - `SUPABASE_SERVICE_ROLE_KEY` = (your Supabase service role key)
     - `USE_IN_MEMORY_DB` = `false`
     - `GOOGLE_API_KEY` = (your Google API key)
     - `AI_MODEL_NAME` = `gemini-1.5-flash`
     - `AI_MOCK` = `false`
     - `CORS_ORIGINS` = (your frontend URL, comma-separated)

4. **Run**
   - Click the "Run" button
   - Replit will automatically use `main.py` as the entry point
   - Your API will be available at the Replit URL

5. **Always On (Optional)**
   - If you have Replit Hacker plan, enable "Always On"
   - This keeps your repl running 24/7

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check endpoint
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login
- `GET /api/users/me` - Get current user
- `GET /api/quiz/questions` - Get quiz questions
- `POST /api/quiz/start` - Start a quiz
- `POST /api/quiz/:quizId/submit` - Submit quiz
- `POST /api/ai/analyze-diagnostic` - Analyze diagnostic results
- And more...

See the codebase for full API documentation.

## Project Structure

```
backend/
├── app.py              # Flask application factory
├── config.py           # Configuration
├── routes/             # API routes
│   ├── users.py
│   ├── quiz.py
│   ├── ai.py
│   └── ...
├── services/           # Business logic
├── utils/              # Utilities
└── repositories/       # Data access layer
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `FLASK_ENV` | Flask environment (development/production) | Yes |
| `SECRET_KEY` | Flask secret key | Yes |
| `SUPABASE_URL` | Supabase project URL | Yes |
| `SUPABASE_ANON_KEY` | Supabase anonymous key | Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase service role key | Yes |
| `USE_IN_MEMORY_DB` | Use in-memory database (false for production) | Yes |
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `AI_MODEL_NAME` | AI model name (gemini-1.5-flash) | No |
| `AI_MOCK` | Use mock AI (false for production) | Yes |
| `CORS_ORIGINS` | Allowed CORS origins | Yes |
| `PORT` | Port number (set by Replit automatically) | No |
| `HOST` | Host (0.0.0.0 for Replit) | No |

## License

See LICENSE file for details.

