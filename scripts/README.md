# Scripts Directory

This directory contains utility scripts for development and testing.

## Test Scripts

### `test_api_powershell.ps1`
PowerShell script for testing API endpoints. Run from project root:
```powershell
.\scripts\test_api_powershell.ps1
```

## Development Scripts

### `run_flask.py`
Run Flask development server with proper logging configuration.
```bash
python scripts/run_flask.py
```

### `run_tests.py`
Run pytest with proper Python path configuration.
```bash
python scripts/run_tests.py
```

## Utility Scripts

### `clear_ai_cache.py`
Clear Flask cache for AI responses (useful for testing real AI calls).
```bash
python scripts/clear_ai_cache.py
```

### `create_test_user_manual.py`
Create a test user in Supabase and get JWT token (requires SERVICE_ROLE_KEY).
```bash
python scripts/create_test_user_manual.py
```

## Database Scripts

### `generate_dummy_questions.py`
Generate dummy questions for testing.
```bash
python scripts/generate_dummy_questions.py
```

### `import_questions.py`
Import questions from JSON file to Supabase.
```bash
python scripts/import_questions.py
```

See `README_QUESTIONS.md` for more details on question management.

## Notes

- All scripts assume they are run from the project root directory
- Scripts use relative imports to access backend modules
- Environment variables should be set in `.env` file in project root

