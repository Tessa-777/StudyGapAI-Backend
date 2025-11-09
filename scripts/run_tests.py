"""
Test runner script that sets up the Python path correctly.
Usage: python run_tests.py [test_file] [pytest_args...]
"""
import sys
from pathlib import Path

# Add project root to Python path (scripts are in scripts/ subdirectory)
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Now run pytest
if __name__ == "__main__":
    import pytest
    
    # Get command line arguments (skip script name)
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    # Default to running all tests if no args provided
    if not args:
        args = ["tests/", "-v"]
    
    # Run pytest with the arguments
    exit_code = pytest.main(args)
    sys.exit(exit_code)

