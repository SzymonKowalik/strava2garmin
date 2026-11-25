import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from dotenv import load_dotenv

# Load last X strava activities
ACTIVITY_LIMIT = 25

# Configure paths
BASE_DIR = Path(__file__).resolve().parent.parent
ACTIVITIES_DIR = BASE_DIR / Path('activities')
DATA_DIR = BASE_DIR / Path('data')
REGISTRY_FILE = 'activity_registry.json'
LOG_FILE = 'strava2garmin.log'

# Ensure directories exist
ACTIVITIES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

REGISTRY_PATH = DATA_DIR / REGISTRY_FILE
LOG_PATH = DATA_DIR / LOG_FILE

# Load .env variables
load_dotenv(BASE_DIR / ".env")

def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise KeyError(f"Missing environment variable {name}. Set it in app/.env (see .env.example).")
    return value


def setup_logging() -> None:
    # Keep at most ~2 MB of logs: the current file plus one 1 MB backup
    file_handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=1, encoding="UTF-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(), file_handler],
        force=True,  # a dependency configures the root logger on import, replace its handler
    )
