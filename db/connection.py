import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not set in .env")


def get_connection():
    """Returns a new psycopg2 connection. Caller must close it."""
    return psycopg2.connect(DATABASE_URL)


def get_cursor(conn):
    """Returns a DictCursor so rows are accessible as dicts."""
    return conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)