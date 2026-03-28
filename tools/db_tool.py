import sqlite3
import json
import os
from typing import List, Optional
from state.schema import ProductItem

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "products.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def search_products(
    category: Optional[str] = None,
    max_price: Optional[float] = None,
    min_rating: float = 4.0,
    limit: int = 5
) -> List[ProductItem]:
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id, title, author, price, rating, category, description, reviews FROM products WHERE 1=1"
    params = []

    if category:
        query += " AND LOWER(category) LIKE ?"
        params.append(f"%{category.lower()}%")

    if max_price:
        query += " AND price <= ?"
        params.append(max_price)

    query += " AND rating >= ?"
    params.append(min_rating)

    query += " ORDER BY rating DESC LIMIT ?"
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    products = []
    for row in rows:
        products.append(ProductItem(
            id=row[0],
            title=row[1],
            author=row[2],
            price=row[3],
            rating=row[4],
            category=row[5],
            description=row[6],
            reviews=json.loads(row[7])
        ))
    return products


def get_product_by_id(product_id: int) -> Optional[ProductItem]:
    conn = get_connection()
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


def place_order(product_id: int, user_id: str = "default_user") -> str:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (product_id, user_id, status) VALUES (?, ?, 'placed')",
        (product_id, user_id)
    )
    conn.commit()
    order_id = f"ORD-{cursor.lastrowid:05d}"
    conn.close()
    return order_id


def get_all_categories() -> List[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM products ORDER BY category")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_price_range() -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(price), MAX(price), AVG(price) FROM products")
    row = cursor.fetchone()
    conn.close()
    return {"min": row[0], "max": row[1], "avg": round(row[2], 2)}
