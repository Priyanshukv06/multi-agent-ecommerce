import sqlite3
import requests
import re
import time
import os

ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT, "data", "products.db")


# ── Same title validation ─────────────────────────────────────────────────────
def is_title_match(ol_title: str, our_title: str) -> bool:
    def clean(t):
        return re.sub(r'[^a-z0-9 ]', '', t.lower().strip())
    ol        = clean(ol_title)
    ours      = clean(our_title)
    our_words = [w for w in ours.split() if len(w) > 2][:3]
    matches   = sum(1 for w in our_words if w in ol)
    return matches >= 2


def try_open_library(title: str, author: str) -> str | None:
    """Try 3 different query formats on Open Library with validation."""
    queries = [
        f"{title} {author}",
        title,
        title.split(":")[0].strip(),
    ]
    for q in queries:
        try:
            resp = requests.get(
                "https://openlibrary.org/search.json",
                params={"q": q, "limit": 5},
                timeout=10
            ).json()
            for doc in resp.get("docs", []):
                if doc.get("cover_i") and is_title_match(doc.get("title", ""), title):
                    cid = doc["cover_i"]
                    return f"https://covers.openlibrary.org/b/id/{cid}-M.jpg"
        except requests.Timeout:
            print(f"      ⏱ OL Timeout: {q[:40]}")
        except Exception as e:
            print(f"      ⚠ OL error: {e}")
        time.sleep(0.3)
    return None


def try_google_books(title: str, author: str) -> str | None:
    """Try 2 different query formats on Google Books with validation."""
    queries = [
        f"intitle:{title.split(':')[0]}+inauthor:{author.split(' ')[-1]}",
        title.split(":")[0].strip(),
    ]
    for q in queries:
        try:
            resp = requests.get(
                "https://www.googleapis.com/books/v1/volumes",
                params={"q": q, "maxResults": 3},
                timeout=10
            ).json()
            for item in resp.get("items", []):
                vol_title = item.get("volumeInfo", {}).get("title", "")
                img       = item.get("volumeInfo", {}).get("imageLinks", {})
                url       = img.get("thumbnail") or img.get("smallThumbnail")
                if url and is_title_match(vol_title, title):
                    return url.replace("http://", "https://")
        except requests.Timeout:
            print(f"      ⏱ GB Timeout: {q[:40]}")
        except Exception as e:
            print(f"      ⚠ GB error: {e}")
        time.sleep(0.3)
    return None


def try_open_library_title_only(title: str) -> str | None:
    """Dedicated title-only search on Open Library with validation."""
    try:
        resp = requests.get(
            "https://openlibrary.org/search.json",
            params={"title": title.split(":")[0].strip(), "limit": 5},
            timeout=10
        ).json()
        for doc in resp.get("docs", []):
            if doc.get("cover_i") and is_title_match(doc.get("title", ""), title):
                return f"https://covers.openlibrary.org/b/id/{doc['cover_i']}-M.jpg"
    except Exception as e:
        print(f"      ⚠ OL title-only error: {e}")
    return None


def retry_missing():
    # ── Fetch ONLY books where cover_url is NULL ──────────────────────────────
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    missing = conn.execute("""
        SELECT id, title, author
        FROM   products
        WHERE  cover_url IS NULL OR cover_url = ''
        ORDER  BY id
    """).fetchall()
    conn.close()

    total = len(missing)

    if total == 0:
        print("✅ No missing covers! All books already have covers.")
        return

    found         = 0
    still_missing = []

    print(f"\n🔄 Retrying {total} missing books...\n{'─'*65}")

    for idx, row in enumerate(missing, 1):
        book_id = row["id"]
        title   = row["title"]
        author  = row["author"]

        print(f"[{idx:>2}/{total}] {title[:50]:<50}", end="  ")

        url = None

        # Strategy 1 — Open Library multi-query
        url = try_open_library(title, author)
        if url:
            print("✅ OpenLibrary")
        else:
            # Strategy 2 — Google Books multi-query
            url = try_google_books(title, author)
            if url:
                print("✅ GoogleBooks")
            else:
                # Strategy 3 — Open Library title-only
                url = try_open_library_title_only(title)
                if url:
                    print("✅ OL TitleSearch")
                else:
                    print("❌ Not found")
                    still_missing.append(title)

        if url:
            found += 1
            # ── ONLY update this specific book row by ID ──────────────────────
            conn = sqlite3.connect(DB_PATH)
            conn.execute(
                "UPDATE products SET cover_url = ? WHERE id = ?",
                (url, book_id)    # surgically update one row only
            )
            conn.commit()
            conn.close()

        time.sleep(0.5)

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{'─'*65}")
    print(f"✅ Newly found  : {found}/{total}")
    print(f"❌ Still missing: {total - found}/{total}")

    if still_missing:
        print(f"\n📋 Genuinely missing (need manual fix):")
        for t in still_missing:
            print(f"  • {t}")
        with open(os.path.join(ROOT, "data", "missing_covers.txt"), "w") as f:
            f.write("\n".join(still_missing))
        print(f"\n💾 Saved to data/missing_covers.txt")

    # ── Final DB stats — just a read, no writes ───────────────────────────────
    conn          = sqlite3.connect(DB_PATH)
    total_books   = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    covered_books = conn.execute(
        "SELECT COUNT(*) FROM products WHERE cover_url IS NOT NULL AND cover_url != ''"
    ).fetchone()[0]
    conn.close()

    print(f"\n📊 DB Coverage: {covered_books}/{total_books} "
          f"({covered_books / total_books * 100:.1f}%)")
    print("✅ fetch_covers_retry.py done. Run fetch_covers_manual.py next.")


if __name__ == "__main__":
    retry_missing()