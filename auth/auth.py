import sqlite3
import bcrypt
import os
from typing import Optional, List, Dict

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'products.db')


def _get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ── Password Helpers ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False


# ── User Queries ──────────────────────────────────────────────────────────────

def get_user_by_username(username: str) -> Optional[Dict]:
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash, role, created_at FROM users WHERE username = ?",
        (username,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> Optional[Dict]:
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, role, created_at FROM users WHERE id = ?",
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def create_user(username: str, password: str, role: str = "user") -> Optional[Dict]:
    conn = _get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {"id": user_id, "username": username, "role": role}
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_all_users() -> List[Dict]:
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, created_at FROM users ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── Order Queries ─────────────────────────────────────────────────────────────

def get_user_orders(user_id: int) -> List[Dict]:
    """All orders with item + product details for a specific user."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            o.order_id,
            o.status,
            o.created_at,
            COALESCE(oi.product_id, 0)         AS product_id,
            COALESCE(oi.quantity,   1)          AS quantity,
            COALESCE(oi.price,      0.0)        AS item_price,
            COALESCE(p.title,  'Unknown Book')  AS title,
            COALESCE(p.author, '')              AS author,
            COALESCE(p.category, '')            AS category,
            COALESCE(p.rating,  0)              AS rating
        FROM orders o
        LEFT JOIN order_items oi ON o.order_id    = oi.order_id
        LEFT JOIN products    p  ON oi.product_id = p.id
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_orders_admin() -> List[Dict]:
    """Admin: all orders across all users."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            o.order_id,
            o.status,
            o.created_at,
            o.user_id,
            COALESCE(u.username, 'unknown')    AS username,
            COALESCE(oi.quantity, 1)           AS quantity,
            COALESCE(oi.price,   0.0)          AS item_price,
            COALESCE(p.title, 'Unknown Book')  AS title
        FROM orders o
        LEFT JOIN users       u  ON o.user_id      = u.id
        LEFT JOIN order_items oi ON o.order_id     = oi.order_id
        LEFT JOIN products    p  ON oi.product_id  = p.id
        ORDER BY o.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_order_status(order_id: str, new_status: str) -> bool:
    """Admin: move an order to a new status."""
    valid = [
        'confirmed', 'packed', 'shipped', 'out_for_delivery', 'delivered',
        'cancelled', 'return_initiated', 'pickup_scheduled', 'picked_up', 'refunded'
    ]
    if new_status not in valid:
        return False
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (new_status, order_id))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


def clear_all_orders() -> int:
    """Admin: wipe all orders/returns. Returns count deleted."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS cnt FROM orders")
    count = cursor.fetchone()["cnt"]
    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM returns")
    cursor.execute("DELETE FROM orders")
    conn.commit()
    conn.close()
    return count


# ── Stock Queries ─────────────────────────────────────────────────────────────

def get_stock(product_id: int) -> int:
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM stock WHERE product_id = ?", (product_id,))
    row = cursor.fetchone()
    conn.close()
    return row["quantity"] if row else 0


def update_stock(product_id: int, new_quantity: int) -> bool:
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO stock (product_id, quantity) VALUES (?, ?) "
        "ON CONFLICT(product_id) DO UPDATE SET quantity = ?",
        (product_id, new_quantity, new_quantity)
    )
    conn.commit()
    conn.close()
    return True