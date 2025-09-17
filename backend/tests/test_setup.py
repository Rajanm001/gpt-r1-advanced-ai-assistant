import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Add the app directory to Python path
app_dir = backend_dir / "app"
sys.path.insert(0, str(app_dir))