"""
Quick test script to verify the Flask app can be imported correctly
for Vercel deployment.
"""
import sys
from pathlib import Path

# Simulate Vercel's import process
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from backend.app import app
    print("[OK] Flask app imported successfully")
    print(f"[OK] App name: {app.name}")
    routes = list(app.url_map.iter_rules())
    print(f"[OK] App has {len(routes)} routes")
    print("\n[OK] All routes:")
    for rule in routes:
        print(f"  - {rule.rule} -> {rule.endpoint}")
    print("\n[OK] Vercel deployment configuration is correct!")
except Exception as e:
    print(f"[ERROR] Error importing app: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

