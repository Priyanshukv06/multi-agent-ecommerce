import json
import os
import sqlite3
from datetime import datetime
from typing import List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "products.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def ensure_memory_table():
    """Create conversation_memory table if it doesn't exist."""
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_memory (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id      TEXT NOT NULL,
            role            TEXT NOT NULL,
            content         TEXT NOT NULL,
            intent          TEXT,
            category        TEXT,
            budget          REAL,
            product_id      INTEGER,
            order_id        TEXT,
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_turn(
    session_id:  str,
    user_query:  str,
    assistant_response: str,
    intent:      Optional[str]  = None,
    category:    Optional[str]  = None,
    budget:      Optional[float]= None,
    product_id:  Optional[int]  = None,
    order_id:    Optional[str]  = None,
):
    """Save one full conversation turn (user + assistant)."""
    ensure_memory_table()
    conn   = get_connection()
    cursor = conn.cursor()

    # Save user message
    cursor.execute("""
        INSERT INTO conversation_memory
        (session_id, role, content, intent, category, budget, product_id, order_id)
        VALUES (?, 'user', ?, ?, ?, ?, ?, ?)
    """, (session_id, user_query, intent, category, budget, product_id, order_id))

    # Save assistant response
    cursor.execute("""
        INSERT INTO conversation_memory
        (session_id, role, content, intent, category, budget, product_id, order_id)
        VALUES (?, 'assistant', ?, ?, ?, ?, ?, ?)
    """, (session_id, assistant_response, intent, category, budget, product_id, order_id))

    conn.commit()
    conn.close()


def get_history(session_id: str, limit: int = 6) -> List[dict]:
    """Get last N turns for a session (N/2 user + N/2 assistant)."""
    ensure_memory_table()
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, intent, category, budget, product_id, order_id, created_at
        FROM conversation_memory
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()

    # Return in chronological order
    rows.reverse()
    return [
        {
            "role":       r[0],
            "content":    r[1],
            "intent":     r[2],
            "category":   r[3],
            "budget":     r[4],
            "product_id": r[5],
            "order_id":   r[6],
            "created_at": r[7],
        }
        for r in rows
    ]


def get_last_context(session_id: str) -> dict:
    """
    Get the most recent useful context from memory:
    last recommended product, category, budget, order_id.
    """
    ensure_memory_table()
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT intent, category, budget, product_id, order_id
        FROM conversation_memory
        WHERE session_id = ?
        ORDER BY id DESC
        LIMIT 10
    """, (session_id,))
    rows = cursor.fetchall()
    conn.close()

    context = {
        "intent":     None,
        "category":   None,
        "budget":     None,
        "product_id": None,
        "order_id":   None,
    }

    for row in rows:
        intent, category, budget, product_id, order_id = row
        if not context["intent"]     and intent:     context["intent"]     = intent
        if not context["category"]   and category:   context["category"]   = category
        if not context["budget"]     and budget:     context["budget"]     = budget
        if not context["product_id"] and product_id: context["product_id"] = product_id
        if not context["order_id"]   and order_id:   context["order_id"]   = order_id

    return context


def clear_session(session_id: str):
    """Clear all memory for a session."""
    ensure_memory_table()
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM conversation_memory WHERE session_id = ?",
        (session_id,)
    )
    conn.commit()
    conn.close()


def format_history_for_prompt(history: List[dict]) -> str:
    """Format conversation history as readable text for LLM context."""
    if not history:
        return "No previous conversation."

    lines = []
    for turn in history[-4:]:   # last 2 exchanges only
        role    = "User"      if turn["role"] == "user" else "Assistant"
        content = turn["content"][:200]   # truncate long responses
        lines.append(f"{role}: {content}")

    return "\n".join(lines)
