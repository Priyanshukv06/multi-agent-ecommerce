from datetime import datetime
from typing import List, Optional
from db.connection import get_connection


def save_turn(
    session_id:         str,
    user_query:         str,
    assistant_response: str,
    intent:      Optional[str]   = None,
    category:    Optional[str]   = None,
    budget:      Optional[float] = None,
    product_id:  Optional[int]   = None,
    order_id:    Optional[str]   = None,
):
    conn   = get_connection()
    cursor = conn.cursor()

    for role, content in [("user", user_query), ("assistant", assistant_response)]:
        cursor.execute("""
            INSERT INTO conversation_memory
            (session_id, role, content, intent, category, budget, product_id, order_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (session_id, role, content, intent, category, budget, product_id, order_id))

    conn.commit()
    conn.close()


def get_history(session_id: str, limit: int = 6) -> List[dict]:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, intent, category, budget, product_id, order_id, created_at
        FROM conversation_memory
        WHERE session_id = %s
        ORDER BY id DESC
        LIMIT %s
    """, (session_id, limit))
    rows = cursor.fetchall()
    conn.close()

    rows.reverse()
    return [
        {
            "role":       r["role"],
            "content":    r["content"],
            "intent":     r["intent"],
            "category":   r["category"],
            "budget":     r["budget"],
            "product_id": r["product_id"],
            "order_id":   r["order_id"],
            "created_at": str(r["created_at"]),
        }
        for r in rows
    ]


def get_last_context(session_id: str) -> dict:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT intent, category, budget, product_id, order_id
        FROM conversation_memory
        WHERE session_id = %s
        ORDER BY id DESC
        LIMIT 10
    """, (session_id,))
    rows = cursor.fetchall()
    conn.close()

    context = {"intent": None, "category": None, "budget": None,
               "product_id": None, "order_id": None}

    for r in rows:
        if not context["intent"]     and r["intent"]:     context["intent"]     = r["intent"]
        if not context["category"]   and r["category"]:   context["category"]   = r["category"]
        if not context["budget"]     and r["budget"]:     context["budget"]     = r["budget"]
        if not context["product_id"] and r["product_id"]: context["product_id"] = r["product_id"]
        if not context["order_id"]   and r["order_id"]:   context["order_id"]   = r["order_id"]

    return context


def clear_session(session_id: str):
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM conversation_memory WHERE session_id = %s", (session_id,))
    conn.commit()
    conn.close()


def format_history_for_prompt(history: List[dict]) -> str:
    if not history:
        return "No previous conversation."

    lines = []
    for turn in history[-4:]:
        role    = "User" if turn["role"] == "user" else "Assistant"
        content = turn["content"][:200]
        lines.append(f"{role}: {content}")

    return "\n".join(lines)