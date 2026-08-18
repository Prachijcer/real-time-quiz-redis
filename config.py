import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Redis Configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
if REDIS_PASSWORD == "":
    REDIS_PASSWORD = None
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Application Configuration
APP_NAME = os.getenv("APP_NAME", "Real-Time Quiz Analytics & Leaderboard System")
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

QUIZZES_FILE = DATA_DIR / "quizzes.json"
QUESTIONS_FILE = DATA_DIR / "questions.json"
USERS_FILE = DATA_DIR / "users.json"
ATTEMPTS_FILE = DATA_DIR / "attempts.json"
