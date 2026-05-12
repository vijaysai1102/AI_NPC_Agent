import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
CAMPUS_CONTEXT_DIR = DATA_DIR / "campus_context"
DB_PATH = DATA_DIR / "campus.db"
NPCS_PATH = DATA_DIR / "npcs.json"

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

MEMORY_CONTEXT_COUNT = 5
RAG_TOP_K = 3
STAT_MIN = 0
STAT_MAX = 100
