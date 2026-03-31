import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import bcrypt
from db.connection import get_connection, get_cursor
from data.seed_products import books          # reuse your existing books list


def seed_products(cursor, conn):
    cursor.execute("SELECT COUNT(*) FROM products")
    if cursor.fetchone()["count"] > 0:
        print("⚠️  Products already seeded — skipping")
        return
    for book in books:
        cursor.execute("""
            INSERT INTO products (title, author, price, rating, category, description, reviews)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            book["title"], book["author"], book["price"],
            book["rating"], book["category"], book["description"],
            json.dumps(book["reviews"])
        ))
    conn.commit()
    print(f"✅ {len(books)} books seeded")


def seed_users(cursor, conn):
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()["count"] > 0:
        print("⚠️  Users already seeded — skipping")
        return

    default_users = [
        ("admin",  "admin123",  "admin"),
        ("user1",  "user123",   "user"),
        ("user2",  "user123",   "user"),
    ]
    for username, password, role in default_users:
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        cursor.execute("""
            INSERT INTO users (username, password_hash, role)
            VALUES (%s, %s, %s)
        """, (username, pw_hash, role))
    conn.commit()
    print(f"✅ {len(default_users)} default users seeded")


if __name__ == "__main__":
    conn   = get_connection()
    cursor = get_cursor(conn)
    seed_products(cursor, conn)
    seed_users(cursor, conn)
    cursor.close()
    conn.close()
    print("✅ Seeding complete")