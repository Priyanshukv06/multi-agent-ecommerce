import sqlite3
import json
import os
import re
from typing import List, Optional
from datetime import datetime, timedelta
from state.schema import ProductItem

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "products.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


# ── Product Operations ─────────────────────────────────────────────────────

def search_products(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    min_rating: float = 4.0,
    limit: int = 5
) -> List[ProductItem]:
    conn   = get_connection()
    cursor = conn.cursor()

    query  = "SELECT id, title, author, price, rating, category, description, reviews FROM products WHERE 1=1"
    params = []

    if category:
        query += " AND LOWER(category) LIKE ?"
        params.append(f"%{category.lower()}%")
    if max_price:
        query += " AND price <= ?"
        params.append(max_price)

    query += " AND rating >= ? ORDER BY rating DESC LIMIT ?"
    params.extend([min_rating, limit])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        ProductItem(
            id=r[0], title=r[1], author=r[2], price=r[3],
            rating=r[4], category=r[5], description=r[6],
            reviews=json.loads(r[7])
        )
        for r in rows
    ]


def get_product_by_id(product_id: int) -> Optional[ProductItem]:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, author, price, rating, category, description, reviews FROM products WHERE id = ?",
        (product_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return ProductItem(
        id=row[0], title=row[1], author=row[2], price=row[3],
        rating=row[4], category=row[5], description=row[6],
        reviews=json.loads(row[7])
    )


def get_all_categories() -> List[str]:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
    rows   = cursor.fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_price_range() -> dict:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM products")
    row    = cursor.fetchone()
    conn.close()
    return {"min": row[0], "max": row[1], "avg": round(row[2], 2)}


# ── Order Operations ───────────────────────────────────────────────────────

def place_order(product_id: int, user_id: str = "default_user") -> str:
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM orders")
    count    = cursor.fetchone()[0]
    order_id = f"ORD-{(count + 1):05d}"

    cursor.execute(
        "INSERT INTO orders (order_id, product_id, user_id, status) VALUES (?, ?, ?, 'confirmed')",
        (order_id, product_id, user_id)
    )
    conn.commit()
    conn.close()
    return order_id


def get_order(order_id: str) -> Optional[dict]:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.order_id, o.product_id, o.user_id, o.status, o.created_at,
               p.title, p.price, p.author
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.order_id = ?
    """, (order_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    created_at  = datetime.strptime(row[4][:19], "%Y-%m-%d %H:%M:%S")
    days_since  = (datetime.now() - created_at).days
    real_status = row[3]   # actual DB status column

    # ── Real status takes priority over time simulation ──────────────────
    if real_status == "return_initiated":
        delivery_status = "Return Initiated — awaiting pickup"
        location        = "Return Processing Center"
    elif real_status == "cancelled":
        delivery_status = "Order Cancelled"
        location        = "N/A"
    elif real_status == "delivered":
        delivery_status = "Delivered ✅"
        location        = "Delivered to customer"
    else:
        # Time-based simulation for active orders
        if days_since == 0:
            delivery_status = "Order Confirmed — being packed"
            location        = "Seller Warehouse"
        elif days_since == 1:
            delivery_status = "Shipped — in transit"
            location        = "Local Sorting Hub"
        elif days_since >= 2:
            delivery_status = "Out for Delivery"
            location        = "Delivery Partner"
        else:
            delivery_status = "Processing"
            location        = "Warehouse"

    eta = (created_at + timedelta(days=5)).strftime("%d %b %Y")

    return {
        "order_id":        row[0],
        "product_id":      row[1],
        "user_id":         row[2],
        "status":          real_status,
        "created_at":      row[4],
        "days_since":      days_since,
        "delivery_status": delivery_status,
        "location":        location,
        "eta":             eta,
        "title":           row[5],
        "price":           row[6],
        "author":          row[7],
    }



def get_user_orders(user_id: str = "default_user") -> List[dict]:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.order_id, o.status, o.created_at, p.title, p.price
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.user_id = ?
        ORDER BY o.created_at DESC
        LIMIT 10
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"order_id": r[0], "status": r[1], "created_at": r[2],
         "title": r[3], "price": r[4]}
        for r in rows
    ]


def cancel_order(order_id: str) -> bool:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET status = 'cancelled' WHERE order_id = ?",
        (order_id,)
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# ── Return Operations ──────────────────────────────────────────────────────

def initiate_return(order_id: str, reason: str = "Not specified",
                    user_id: str = "default_user") -> Optional[str]:
    """Returns return_id if eligible, None if not found or not eligible."""
    conn   = get_connection()
    cursor = conn.cursor()

    # Check order exists and belongs to user
    cursor.execute(
        "SELECT status, created_at FROM orders WHERE order_id = ? AND user_id = ?",
        (order_id, user_id)
    )
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    status, created_at = row
    created_dt  = datetime.strptime(created_at[:19], "%Y-%m-%d %H:%M:%S")
    days_since  = (datetime.now() - created_dt).days
    return_window = 7   # 7-day return policy

    if days_since > return_window:
        conn.close()
        return "EXPIRED"

    if status == "cancelled":
        conn.close()
        return "ALREADY_CANCELLED"

    # Check if return already initiated
    cursor.execute("SELECT return_id FROM returns WHERE order_id = ?", (order_id,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing[0]   # return existing return_id

    # Create return
    cursor.execute("SELECT COUNT(*) FROM returns")
    count     = cursor.fetchone()[0]
    return_id = f"RET-{(count + 1):05d}"

    cursor.execute(
        "INSERT INTO returns (return_id, order_id, user_id, reason, status) VALUES (?, ?, ?, ?, 'initiated')",
        (return_id, order_id, user_id, reason)
    )
    cursor.execute(
        "UPDATE orders SET status = 'return_initiated' WHERE order_id = ?",
        (order_id,)
    )
    conn.commit()
    conn.close()
    return return_id


def get_return_status(return_id: str) -> Optional[dict]:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT return_id, order_id, status, reason, created_at FROM returns WHERE return_id = ?",
        (return_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "return_id":  row[0], "order_id": row[1],
        "status":     row[2], "reason":   row[3],
        "created_at": row[4]
    }
