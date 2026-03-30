import sqlite3
import requests
import time
import re
import os

ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT, "data", "products.db")


# ── Title validation ──────────────────────────────────────────────────────────
def is_title_match(ol_title: str, our_title: str) -> bool:
    def clean(t):
        return re.sub(r'[^a-z0-9 ]', '', t.lower().strip())
    ol        = clean(ol_title)
    ours      = clean(our_title)
    our_words = [w for w in ours.split() if len(w) > 2][:3]
    matches   = sum(1 for w in our_words if w in ol)
    return matches >= 2


# ── These functions return (url_or_None, status_reason) ──────────────────────
# NO print statements inside — caller handles all printing

def fetch_open_library(title: str, author: str) -> tuple[str | None, str]:
    try:
        resp = requests.get(
            "https://openlibrary.org/search.json",
            params={"q": f"{title} {author}", "limit": 5},
            timeout=6
        ).json()
        for doc in resp.get("docs", []):
            if doc.get("cover_i") and is_title_match(doc.get("title", ""), title):
                url = f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
                return url, "OpenLibrary"
        return None, "OL:no_match"
    except requests.Timeout:
        return None, "OL:timeout"
    except Exception as e:
        return None, f"OL:error"


def fetch_google_books(title: str, author: str) -> tuple[str | None, str]:
    try:
        query = f"intitle:{title.split(':')[0]}+inauthor:{author.split(' ')[-1]}"
        resp  = requests.get(
            "https://www.googleapis.com/books/v1/volumes",
            params={"q": query, "maxResults": 3},
            timeout=6
        ).json()
        for item in resp.get("items", []):
            vol_title = item.get("volumeInfo", {}).get("title", "")
            img       = item.get("volumeInfo", {}).get("imageLinks", {})
            url       = img.get("thumbnail") or img.get("smallThumbnail")
            if url and is_title_match(vol_title, title):
                return url.replace("http://", "https://"), "GoogleBooks"
        return None, "GB:no_match"
    except requests.Timeout:
        return None, "GB:timeout"
    except Exception as e:
        return None, "GB:error"


def fetch_all_covers():
    # ── Add cover_url column if missing ──────────────────────────────────────
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("ALTER TABLE products ADD COLUMN cover_url TEXT")
        conn.commit()
        print("✅ cover_url column added.")
    except Exception:
        print("ℹ️  cover_url column already exists.")
    conn.close()

    # ── Load all books ────────────────────────────────────────────────────────
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    books = conn.execute(
        "SELECT id, title, author FROM products ORDER BY id"
    ).fetchall()
    conn.close()

    total   = len(books)
    found   = 0
    missing = []

    print(f"\n📚 Fetching covers for {total} books...\n{'─'*70}")

    for idx, row in enumerate(books, 1):
        book_id = row["id"]
        title   = row["title"]
        author  = row["author"]

        # Print title line — NO newline yet
        print(f"[{idx:>3}/{total}] {title[:48]:<48}", end="  ")

        # Try Open Library
        url, reason = fetch_open_library(title, author)

        # Fallback to Google Books only if OL failed
        if not url:
            url, reason = fetch_google_books(title, author)

        # ── Update only this book row by ID ───────────────────────────────────
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "UPDATE products SET cover_url = ? WHERE id = ?",
            (url, book_id)
        )
        conn.commit()
        conn.close()

        # Print result on SAME line as title
        if url:
            found += 1
            print(f"✅ {reason}")
        else:
            missing.append(title)
            print(f"❌ {reason}")        # shows exactly WHY it failed

        time.sleep(0.4)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'─'*70}")
    print(f"✅ Found   : {found}/{total} ({found/total*100:.1f}%)")
    print(f"❌ Missing : {total - found}/{total}")

    if missing:
        print("\nBooks without covers:")
        for t in missing:
            print(f"  • {t}")

    print("\n✅ Done. Run fetch_covers_retry.py next for missing ones.")


if __name__ == "__main__":
    fetch_all_covers()