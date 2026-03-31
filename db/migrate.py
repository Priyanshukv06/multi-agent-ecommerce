import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.connection import get_connection, get_cursor


def run_migrations():
    conn   = get_connection()
    cursor = get_cursor(conn)

    # ── Products ──────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id          SERIAL PRIMARY KEY,
            title       TEXT    NOT NULL,
            author      TEXT    NOT NULL,
            price       REAL    NOT NULL,
            rating      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            description TEXT    NOT NULL,
            reviews     TEXT    NOT NULL,
            cover_url   TEXT,
            stock       INTEGER NOT NULL DEFAULT 10
        )
    """)

    # ── Users ─────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id            SERIAL PRIMARY KEY,
            username      TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role          TEXT NOT NULL DEFAULT 'user',
            created_at    TIMESTAMP DEFAULT NOW()
        )
    """)

    # ── Orders ────────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id         SERIAL PRIMARY KEY,
            order_id   TEXT    NOT NULL UNIQUE,
            product_id INTEGER NOT NULL REFERENCES products(id),
            user_id    INTEGER NOT NULL REFERENCES users(id),
            quantity   INTEGER NOT NULL DEFAULT 1,
            item_price REAL    NOT NULL DEFAULT 0,
            status     TEXT    NOT NULL DEFAULT 'confirmed',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # ── Returns ───────────────────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS returns (
            id         SERIAL PRIMARY KEY,
            return_id  TEXT NOT NULL UNIQUE,
            order_id   TEXT NOT NULL REFERENCES orders(order_id),
            user_id    INTEGER NOT NULL REFERENCES users(id),
            reason     TEXT,
            status     TEXT NOT NULL DEFAULT 'initiated',
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    # ── Conversation History ───────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversation_history (
            id         SERIAL PRIMARY KEY,
            session_id TEXT    NOT NULL,
            role       TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            intent     TEXT,
            category   TEXT,
            budget     REAL,
            product_id INTEGER,
            order_id   TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ All tables created in PostgreSQL")


if __name__ == "__main__":
    run_migrations()