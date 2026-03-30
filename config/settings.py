import os
import sys
from dotenv import load_dotenv

# Load .env from project root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(ROOT, '.env'))


# ── Helper ────────────────────────────────────────────────────────────────────
def _require(key: str) -> str:
    """Get env var or exit with clear error — no silent failures."""
    val = os.getenv(key, "").strip()
    if not val:
        print(f"\n❌ ERROR: Missing required environment variable: {key}")
        print(f"   Add it to your .env file and restart.\n")
        sys.exit(1)
    return val

def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default).strip()


# ── LLM Keys (required) ───────────────────────────────────────────────────────
NVIDIA_API_KEY: str = _require("NVIDIA_API_KEY")
GROQ_API_KEY:   str = _require("GROQ_API_KEY")

# ── App Security (required) ───────────────────────────────────────────────────
SECRET_KEY: str = _require("SECRET_KEY")

# ── App Config (optional with sensible defaults) ──────────────────────────────
APP_ENV:      str  = _optional("APP_ENV",      "development")
API_BASE_URL: str  = _optional("API_BASE_URL", "http://localhost:8000/api/v1")
DEBUG:        bool = _optional("DEBUG", "true").lower() == "true"

# ── DB Path ───────────────────────────────────────────────────────────────────
DB_PATH: str = os.path.join(ROOT, "data", "products.db")


# ── Startup validation summary ────────────────────────────────────────────────
def print_config_summary():
    print(f"\n{'─'*50}")
    print(f"⚙️  Config Loaded")
    print(f"   ENV        : {APP_ENV}")
    print(f"   API URL    : {API_BASE_URL}")
    print(f"   DEBUG      : {DEBUG}")
    print(f"   NVIDIA KEY : {'✅ set' if NVIDIA_API_KEY else '❌ missing'}")
    print(f"   GROQ KEY   : {'✅ set' if GROQ_API_KEY else '❌ missing'}")
    print(f"   SECRET KEY : {'✅ set' if SECRET_KEY else '❌ missing'}")
    print(f"{'─'*50}\n")