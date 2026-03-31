import json
from typing import List, Optional
from datetime import datetime, timedelta
from state.schema import ProductItem
from db.connection import get_connection


# ── Product Operations ────────────────────────────────────────────────────────

def search_products(
    category:   Optional[str]   = None,
    max_price:  Optional[float] = None,
    min_rating: float           = 4.0,
    limit:      int             = 5
) -> List[ProductItem]:
    conn   = get_connection()
    cursor = conn.cursor()

    query  = """
        SELECT id, title, author, price, rating, category,
               description, reviews, cover_url
        FROM products
        WHERE 1=1
    """
    params = []

    if category:
        query += " AND LOWER(category) LIKE %s"
        params.append(f"%{category.lower()}%")
    if max_price:
        query += " AND price <= %s"
        params.append(max_price)

    query += " AND rating >= %s ORDER BY rating DESC LIMIT %s"
    params.extend([min_rating, limit])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [
        ProductItem(
            id=r["id"], title=r["title"], author=r["author"],
            price=r["price"], rating=r["rating"], category=r["category"],
            description=r["description"],
            reviews=r["reviews"] if isinstance(r["reviews"], list) else json.loads(r["reviews"]),
            cover_url=r["cover_url"]
        )
        for r in rows
    ]


def get_product_by_id(product_id: int) -> Optional[ProductItem]:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, author, price, rating, category,
               description, reviews, cover_url
        FROM products WHERE id = %s
    """, (product_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return ProductItem(
        id=row["id"], title=row["title"], author=row["author"],
        price=row["price"], rating=row["rating"], category=row["category"],
        description=row["description"],
        reviews=row["reviews"] if isinstance(row["reviews"], list) else json.loads(row["reviews"]),
        cover_url=row["cover_url"]
    )


def get_all_categories() -> List[str]:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
    rows = cursor.fetchall()
    conn.close()
    return [r["category"] for r in rows]


def get_price_range() -> dict:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM products")
    row = cursor.fetchone()
    conn.close()
    return {"min": row["min"], "max": row["max"], "avg": round(row["avg"], 2)}


# ── Order Operations ──────────────────────────────────────────────────────────

def place_order(product_id: int, user_id: str = "default_user") -> str:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS cnt FROM orders")
    count    = cursor.fetchone()["cnt"]
    order_id = f"ORD-{count + 1:05d}"
    cursor.execute(
        "INSERT INTO orders (order_id, product_id, user_id, status) VALUES (%s, %s, %s, %s)",
        (order_id, product_id, user_id, "confirmed")
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
        WHERE o.order_id = %s
    """, (order_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    created_at = row["created_at"]
    if isinstance(created_at, str):
        created_at = datetime.strptime(created_at[:19], "%Y-%m-%d %H:%M:%S")

    days_since = (datetime.now() - created_at).days

    if days_since == 0:
        delivery_status = "Order Confirmed — being packed"
        location        = "Seller Warehouse"
    elif days_since == 1:
        delivery_status = "Shipped — in transit"
        location        = "Local Sorting Hub"
    elif days_since == 2:
        delivery_status = "Out for Delivery"
        location        = "Delivery Partner"
    else:
        delivery_status = "Processing"
        location        = "Warehouse"

    eta = (created_at + timedelta(days=5)).strftime("%d %b %Y")

    return {
        "order_id":        row["order_id"],
        "product_id":      row["product_id"],
        "user_id":         row["user_id"],
        "status":          row["status"],
        "created_at":      str(row["created_at"]),
        "days_since":      days_since,
        "delivery_status": delivery_status,
        "location":        location,
        "eta":             eta,
        "title":           row["title"],
        "price":           row["price"],
        "author":          row["author"],
    }


def get_user_orders(user_id: str = "default_user") -> List[dict]:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT o.order_id, o.status, o.created_at, p.title, p.price
        FROM orders o
        JOIN products p ON o.product_id = p.id
        WHERE o.user_id = %s
        ORDER BY o.created_at DESC
        LIMIT 10
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {"order_id": r["order_id"], "status": r["status"],
         "created_at": str(r["created_at"]), "title": r["title"], "price": r["price"]}
        for r in rows
    ]


def cancel_order(order_id: str) -> bool:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET status='cancelled' WHERE order_id=%s",
        (order_id,)
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


# ── Return Operations ─────────────────────────────────────────────────────────

def initiate_return(
    order_id: str,
    reason:   str = "Not specified",
    user_id:  str = "default_user"
) -> Optional[str]:
    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT status, created_at FROM orders WHERE order_id=%s AND user_id=%s",
        (order_id, user_id)
    )
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    created_at = row["created_at"]
    if isinstance(created_at, str):
        created_at = datetime.strptime(created_at[:19], "%Y-%m-%d %H:%M:%S")

    days_since = (datetime.now() - created_at).days

    if days_since > 7:
        conn.close()
        return "EXPIRED"
    if row["status"] == "cancelled":
        conn.close()
        return "ALREADY_CANCELLED"

    cursor.execute("SELECT return_id FROM returns WHERE order_id=%s", (order_id,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return existing["return_id"]

    cursor.execute("SELECT COUNT(*) AS cnt FROM returns")
    count     = cursor.fetchone()["cnt"]
    return_id = f"RET-{count + 1:05d}"

    cursor.execute(
        "INSERT INTO returns (return_id, order_id, user_id, reason, status) "
        "VALUES (%s, %s, %s, %s, %s)",
        (return_id, order_id, user_id, reason, "initiated")
    )
    cursor.execute(
        "UPDATE orders SET status='return_initiated' WHERE order_id=%s",
        (order_id,)
    )
    conn.commit()
    conn.close()
    return return_id


def get_return_status(return_id: str) -> Optional[dict]:
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT return_id, order_id, status, reason, created_at "
        "FROM returns WHERE return_id=%s",
        (return_id,)
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "return_id":  row["return_id"],
        "order_id":   row["order_id"],
        "status":     row["status"],
        "reason":     row["reason"],
        "created_at": str(row["created_at"]),
    }