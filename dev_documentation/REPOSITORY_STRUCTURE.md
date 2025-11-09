# Repository Structure

## Directory Layout

```
Royal-Light-StudyGapAI/
├── backend/                 # Backend application code
│   ├── routes/             # API routes
│   ├── services/           # Business logic and AI services
│   ├── repositories/       # Database repositories
│   └── utils/              # Utility functions
├── tests/                  # All test files
│   ├── test_ai_se_integration.py    # Pytest unit tests
│   ├── test_app_endpoints.py        # Pytest endpoint tests
│   └── test_*.py           # Manual/integration test scripts
├── scripts/                # Utility and development scripts
│   ├── run_flask.py        # Flask development server
│   ├── run_tests.py        # Test runner
│   └── *.py                # Other utility scripts
├── supabase/               # Database migrations
│   └── migrations/         # SQL migration files
├── dev_documentation/      # Development documentation
├── Procfile                # Render deployment configuration
├── runtime.txt             # Python version for Render
├── requirements.txt        # Python dependencies
├── env.example             # Environment variables template
└── README.md               # Project overview
```

## Key Files

### Configuration Files
- `Procfile` - Render deployment configuration
- `runtime.txt` - Python version (3.11.9)
- `requirements.txt` - Python dependencies
- `pytest.ini` - Pytest configuration
- `env.example` - Environment variables template
- `.gitignore` - Git ignore rules

### Documentation
- `README.md` - Project overview
- `RENDER_DEPLOYMENT_GUIDE.md` - Deployment guide
- `DEPLOYMENT_READY.md` - Deployment status
- `REPOSITORY_STRUCTURE.md` - This file
- `dev_documentation/` - Development documentation

### Scripts
- `scripts/run_flask.py` - Run Flask development server
- `scripts/run_tests.py` - Run tests with proper path
- `scripts/clear_ai_cache.py` - Clear AI cache
- `scripts/create_test_user_manual.py` - Create test user
- See `scripts/README.md` for details

### Tests
- `tests/test_ai_se_integration.py` - AI/SE integration tests
- `tests/test_app_endpoints.py` - API endpoint tests
- `tests/test_*.py` - Manual/integration test scripts
- See `tests/README.md` for details

## Running the Application

### Development Server
```bash
python scripts/run_flask.py
# or
flask run
```

### Run Tests
```bash
python scripts/run_tests.py
# or
pytest tests/ -v
```

### Run Manual Test Scripts
```bash
python tests/test_ai_config.py
python tests/test_diagnostic_api.py
# etc.
```

## Deployment

See `RENDER_DEPLOYMENT_GUIDE.md` for deployment instructions.

## Notes

- All test files are in `tests/` directory
- All utility scripts are in `scripts/` directory
- Backend code is in `backend/` directory
- Database migrations are in `supabase/migrations/`
- Documentation is in `dev_documentation/` directory

