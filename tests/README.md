# Tests Directory

This directory contains all test files for the StudyGapAI backend.

## Test Structure

### Unit Tests (Pytest)

- `test_ai_se_integration.py` - AI/SE integration tests
- `test_app_endpoints.py` - API endpoint tests

These tests are run with pytest:
```bash
pytest tests/ -v
```

### Integration/Manual Test Scripts

These are manual/integration test scripts that require a running Flask server. They are prefixed with `manual_test_` so pytest doesn't try to run them:

- `manual_test_ai_config.py` - Diagnostic script for AI configuration
- `manual_test_diagnostic_api.py` - Complete diagnostic API test
- `manual_test_guest_mode.py` - Guest mode functionality test
- `manual_test_save_diagnostic.py` - Save diagnostic endpoint test
- `manual_test_save_diagnostic_complete.py` - Complete save diagnostic flow test
- `manual_test_real_ai_call.py` - Real AI API call test

**Note:** These scripts are NOT run by pytest. They are manual integration tests that require a running Flask server.

Run them directly:
```bash
# Start Flask server first
python scripts/run_flask.py

# Then in another terminal, run the manual test
python tests/manual_test_ai_config.py
python tests/manual_test_diagnostic_api.py
python tests/manual_test_guest_mode.py
python tests/manual_test_save_diagnostic.py
python tests/manual_test_save_diagnostic_complete.py
python tests/manual_test_real_ai_call.py
```

## Running Tests

### Run All Pytest Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_ai_se_integration.py -v
```

### Run with Coverage
```bash
pytest tests/ -v --cov=backend --cov-report=html
```

### Run Manual Test Scripts
```bash
python tests/test_ai_config.py
python tests/test_diagnostic_api.py
python tests/test_guest_mode.py
python tests/test_save_diagnostic.py
python tests/test_save_diagnostic_complete.py
python tests/test_real_ai_call.py
```

## Test Configuration

- `conftest.py` - Pytest configuration and fixtures
- `pytest.ini` - Pytest settings (in project root)

## Environment Variables

Tests require environment variables to be set in `.env` file:
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `GOOGLE_API_KEY` (for real AI tests)
- `AI_MOCK=true` (for mock AI tests)

## Notes

- All tests use the `conftest.py` configuration
- Tests can use in-memory repository (`USE_IN_MEMORY_DB=true`) or Supabase
- Integration tests require a running Flask server (default: `http://localhost:5000`)

