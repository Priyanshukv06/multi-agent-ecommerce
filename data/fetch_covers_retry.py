import sqlite3
import requests
import time
import os

ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT, "data", "products.db")

# ── Fetch strategies (tries multiple query formats) ───────────────────────────

def try_open_library(title: str, author: str) -> str | None:
    """Try 3 different query formats on Open Library."""
    queries = [
        f"{title} {author}",           # full query
        title,                          # title only
        f"{title.split(':')[0]}",       # title before colon (e.g. "Fluent Python")
    ]
    for q in queries:
        try:
            resp = requests.get(
                f"https://openlibrary.org/search.json",
                params={"q": q, "limit": 3},
                timeout=10
            ).json()
            docs = resp.get("docs", [])
            for doc in docs:
                if doc.get("cover_i"):
                    cid = doc["cover_i"]
                    return f"https://covers.openlibrary.org/b/id/{cid}-M.jpg"
        except requests.Timeout:
            print(f"      ⏱ Timeout on OL query: {q[:40]}")
        except Exception as e:
            print(f"      ⚠ OL error: {e}")
        time.sleep(0.3)
    return None


def try_google_books(title: str, author: str) -> str | None:
    """Try 2 different query formats on Google Books."""
    queries = [
        f"intitle:{title.split(':')[0]}+inauthor:{author.split(' ')[-1]}",
        f"{title.split(':')[0]}",
    ]
    for q in queries:
        try:
            resp = requests.get(
                "https://www.googleapis.com/books/v1/volumes",
                params={"q": q, "maxResults": 3},
                timeout=10
            ).json()
            for item in resp.get("items", []):
                img = item.get("volumeInfo", {}).get("imageLinks", {})
                url = img.get("thumbnail") or img.get("smallThumbnail")
                if url:
                    return url.replace("http://", "https://")
        except requests.Timeout:
            print(f"      ⏱ Timeout on GB query: {q[:40]}")
        except Exception as e:
            print(f"      ⚠ GB error: {e}")
        time.sleep(0.3)
    return None


def try_open_library_isbn(title: str) -> str | None:
    """Search by title on Open Library works API."""
    try:
        resp = requests.get(
            "https://openlibrary.org/search.json",
            params={"title": title.split(":")[0].strip(), "limit": 5},
            timeout=10
        ).json()
        for doc in resp.get("docs", []):
            if doc.get("cover_i"):
                return f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
    except Exception as e:
        print(f"      ⚠ OL title search error: {e}")
    return None


# ── Main retry logic ──────────────────────────────────────────────────────────

def retry_missing():
    conn  = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # Get only books with no cover_url
    missing = conn.execute("""
        SELECT id, title, author
        FROM products
        WHERE cover_url IS NULL OR cover_url = ''
        ORDER BY id
    """).fetchall()
    conn.close()

    total   = len(missing)
    found   = 0
    still_missing = []

    print(f"\n🔄 Retrying {total} missing books...\n{'─'*65}")

    for idx, row in enumerate(missing, 1):
        book_id = row["id"]
        title   = row["title"]
        author  = row["author"]

        print(f"[{idx:>2}/{total}] {title[:50]:<50}", end="  ")

        url = None

        # Strategy 1 — Open Library (multi-query)
        url = try_open_library(title, author)
        if url:
            print(f"✅ OpenLibrary")
        else:
            # Strategy 2 — Google Books (multi-query)
            url = try_google_books(title, author)
            if url:
                print(f"✅ GoogleBooks")
            else:
                # Strategy 3 — Open Library title-only API
                url = try_open_library_isbn(title)
                if url:
                    print(f"✅ OL TitleSearch")
                else:
                    print(f"❌ Not found")
                    still_missing.append(title)

        if url:
            found += 1
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "UPDATE products SET cover_url=? WHERE id=?",
                (url, book_id)
            )
            conn.commit()
            conn.close()

        time.sleep(0.5)   # slightly longer delay for reliability

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'─'*65}")
    print(f"✅ Newly found : {found}/{total}")
    print(f"❌ Still missing: {total - found}/{total}")

    if still_missing:
        print(f"\n📋 Genuinely missing (need manual fix):")
        for t in still_missing:
            print(f"  • {t}")

        # Save to a txt file for manual handling
        with open(os.path.join(ROOT, "data", "missing_covers.txt"), "w") as f:
            f.write("\n".join(still_missing))
        print(f"\n💾 Saved to data/missing_covers.txt")

    # ── Final DB stats ────────────────────────────────────────────────────────
    conn  = sqlite3.connect(DB_PATH)
    total_books   = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    covered_books = conn.execute(
        "SELECT COUNT(*) FROM products WHERE cover_url IS NOT NULL AND cover_url != ''"
    ).fetchone()[0]
    conn.close()

    print(f"\n📊 Final DB Coverage: {covered_books}/{total_books} "
          f"({covered_books/total_books*100:.1f}%)")
    print("🎉 Retry complete!")


if __name__ == "__main__":
    retry_missing()