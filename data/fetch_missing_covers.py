import sys
import os
import time
import httpx

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, ROOT)

from db.connection import get_connection


# ══════════════════════════════════════════════════════
# SOURCE 1 — Open Library
# ══════════════════════════════════════════════════════
def fetch_openlibrary(title: str, author: str) -> str | None:
    try:
        query = f"{title} {author}".replace(" ", "+")
        resp  = httpx.get(
            f"https://openlibrary.org/search.json"
            f"?q={query}&limit=1&fields=cover_i",
            timeout=6.0
        )
        if resp.status_code == 200:
            docs    = resp.json().get("docs", [])
            cover_i = docs[0].get("cover_i") if docs else None
            if cover_i:
                return f"https://covers.openlibrary.org/b/id/{cover_i}-M.jpg"
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════════════
# SOURCE 2 — Google Books API (no key needed)
# ══════════════════════════════════════════════════════
def fetch_google_books(title: str, author: str) -> str | None:
    try:
        query = f"intitle:{title} inauthor:{author}".replace(" ", "+")
        resp  = httpx.get(
            f"https://www.googleapis.com/books/v1/volumes"
            f"?q={query}&maxResults=1&fields=items/volumeInfo/imageLinks",
            timeout=6.0
        )
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            if items:
                links = items[0].get("volumeInfo", {}).get("imageLinks", {})
                # Prefer large → medium → thumbnail, upgrade to higher res
                url = (
                    links.get("large") or
                    links.get("medium") or
                    links.get("thumbnail") or
                    links.get("smallThumbnail")
                )
                if url:
                    # Force HTTPS + remove curl parameter for higher res
                    url = url.replace("http://", "https://")
                    url = url.replace("&edge=curl", "")
                    # Upgrade to zoom=1 for larger image
                    url = url.replace("zoom=1", "zoom=2") \
                             if "zoom=" in url else url + "&zoom=2"
                    return url
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════════════
# COMBINED — tries both sources with retry
# ══════════════════════════════════════════════════════
def fetch_cover_with_fallback(
    title: str,
    author: str,
    retries: int = 2
) -> tuple[str | None, str]:
    """
    Returns (url, source) where source is one of:
    'openlibrary', 'google_books', 'not_found'
    """
    for attempt in range(retries):
        # ── Try Open Library first ────────────────────
        url = fetch_openlibrary(title, author)
        if url:
            return url, "openlibrary"

        # ── Fallback: Google Books ────────────────────
        url = fetch_google_books(title, author)
        if url:
            return url, "google_books"

        # ── Retry wait ────────────────────────────────
        if attempt < retries - 1:
            time.sleep(2.0)

    return None, "not_found"


# ══════════════════════════════════════════════════════
# PATCH MISSING COVERS IN DB
# ══════════════════════════════════════════════════════
def patch_missing_covers():
    conn   = get_connection()
    cursor = conn.cursor()

    # Fetch only books with missing cover_url
    cursor.execute("""
        SELECT id, title, author
        FROM products
        WHERE cover_url IS NULL OR cover_url = ''
        ORDER BY id
    """)
    missing = cursor.fetchall()

    if not missing:
        print("✅ All books already have covers! Nothing to patch.")
        conn.close()
        return

    total    = len(missing)
    found    = 0
    ol_count = 0
    gb_count = 0
    failed   = []

    print(f"\n🔍 Found {total} books with missing covers. Fetching...\n")

    for i, (pid, title, author) in enumerate(missing, 1):
        url, source = fetch_cover_with_fallback(title, author)

        if url:
            cursor.execute(
                "UPDATE products SET cover_url = %s WHERE id = %s",
                (url, pid)
            )
            found += 1
            if source == "openlibrary":
                ol_count += 1
                icon = "📗"
            else:
                gb_count += 1
                icon = "📘"
            print(f"  [{i:>2}/{total}] {icon} [{source:<12}] {title[:45]}")
        else:
            failed.append((pid, title))
            print(f"  [{i:>2}/{total}] ❌ [not_found  ] {title[:45]}")

        conn.commit()                      # commit after each — safe on crash
        time.sleep(1.0)                    # polite rate limit

    cursor.close()
    conn.close()

    # ── Summary ──────────────────────────────────────
    print(f"\n{'='*55}")
    print(f"✅ Covers patched successfully!")
    print(f"{'='*55}")
    print(f"  Total missing    : {total}")
    print(f"  ✅ Found         : {found}/{total}")
    print(f"    📗 Open Library : {ol_count}")
    print(f"    📘 Google Books : {gb_count}")
    print(f"  ❌ Still missing : {total - found}")

    if failed:
        print(f"\n  Books still without covers:")
        for pid, title in failed:
            print(f"    ID {pid:>3}: {title}")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    patch_missing_covers()