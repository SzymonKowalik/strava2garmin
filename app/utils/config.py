from pathlib import Path
from dotenv import load_dotenv

# Load last X strava activities
ACTIVITY_LIMIT = 25

# Configure paths
BASE_DIR = Path(__file__).resolve().parent.parent
ACTIVITIES_DIR = BASE_DIR / Path('activities')
DATA_DIR = BASE_DIR / Path('data')
REGISTRY_FILE = 'activity_registry.json'

# Load .env variables
load_dotenv(BASE_DIR / ".env")

# Ensure directories exist
ACTIVITIES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_PATH = DATA_DIR / REGISTRY_FILE
