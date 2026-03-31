import os
import sys
from dotenv import load_dotenv


# Load .env from project root (local dev only — ignored on cloud)
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(ROOT, '.env'))


# ── Helper: reads from st.secrets (cloud) → .env (local) ─────────────────────
def _get(key: str, default: str = "") -> str:
    # Try Streamlit secrets first (Streamlit Cloud deployment)
    try:
        import streamlit as st
        if key in st.secrets:
            return str(st.secrets[key]).strip()
    except Exception:
        pass
    # Fall back to environment variable / .env
    return os.getenv(key, default).strip()


def _require(key: str) -> str:
    """Get env var or exit with clear error — no silent failures."""
    val = _get(key)                              # ← FIXED: was os.getenv only
    if not val:
        print(f"\n❌ ERROR: Missing required environment variable: {key}")
        print(f"   Add it to your .env file (local) or secrets (cloud).\n")
        sys.exit(1)
    return val


def _optional(key: str, default: str = "") -> str:
    return _get(key, default)                    # ← FIXED: was os.getenv only


# ── LLM Keys (required) ───────────────────────────────────────────────────────
NVIDIA_API_KEY: str = _require("NVIDIA_API_KEY")
GROQ_API_KEY:   str = _require("GROQ_API_KEY")


# ── App Security (required) ───────────────────────────────────────────────────
SECRET_KEY: str = _require("SECRET_KEY")


# ── App Config (optional with sensible defaults) ──────────────────────────────
APP_ENV:      str  = _optional("APP_ENV",   "development")
DEBUG:        bool = _optional("DEBUG",     "true").lower() == "true"

# ← FIXED: reads API_URL from secrets, falls back to localhost
API_BASE_URL: str  = _optional("API_URL",   "http://localhost:8000").rstrip("/") + "/api/v1"


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