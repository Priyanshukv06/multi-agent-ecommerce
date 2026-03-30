import sqlite3
import os

ROOT    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DB_PATH = os.path.join(ROOT, "data", "products.db")

# ── Hardcoded ISBN-based covers (100% reliable) ───────────────────────────────
# Format: https://covers.openlibrary.org/b/isbn/{ISBN}-M.jpg
# Or direct Google Books thumbnail URLs as fallback

MANUAL_COVERS = {
    "Machine Learning Design Patterns": 
        "https://covers.openlibrary.org/b/isbn/9781098115784-M.jpg",

    "Programming PyTorch for Deep Learning":
        "https://covers.openlibrary.org/b/isbn/9781492045359-M.jpg",

    "Mastering spaCy":
        "https://covers.openlibrary.org/b/isbn/9781800563353-M.jpg",

    "Introduction to Algorithms (CLRS)":
        "https://covers.openlibrary.org/b/isbn/9780262033848-M.jpg",

    "ML Engineering with Python":
        "https://covers.openlibrary.org/b/isbn/9781801079259-M.jpg",

    "Learning OpenCV 4":
        "https://covers.openlibrary.org/b/isbn/9781492051213-M.jpg",

    "Practical Deep Learning for Cloud and Mobile":
        "https://covers.openlibrary.org/b/isbn/9781492034858-M.jpg",
}


def apply_manual_covers():
    conn  = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    print(f"\n🔧 Applying manual covers for {len(MANUAL_COVERS)} books...\n{'─'*65}")

    fixed = 0
    for title, url in MANUAL_COVERS.items():
        result = conn.execute(
            "UPDATE products SET cover_url=? WHERE title=?",
            (url, title)
        )
        conn.commit()

        if result.rowcount > 0:
            fixed += 1
            print(f"✅ {title[:55]}")
        else:
            # Try partial match (in case title has slight variation in DB)
            result2 = conn.execute(
                "UPDATE products SET cover_url=? WHERE title LIKE ?",
                (url, f"%{title[:30]}%")
            )
            conn.commit()
            if result2.rowcount > 0:
                fixed += 1
                print(f"✅ {title[:55]}  (partial match)")
            else:
                print(f"⚠️  Not found in DB: {title[:55]}")

    conn.close()

    # ── Final stats ───────────────────────────────────────────────────────────
    conn = sqlite3.connect(DB_PATH)
    total   = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    covered = conn.execute(
        "SELECT COUNT(*) FROM products "
        "WHERE cover_url IS NOT NULL AND cover_url != ''"
    ).fetchone()[0]
    still_missing = conn.execute(
        "SELECT title FROM products "
        "WHERE cover_url IS NULL OR cover_url = ''"
    ).fetchall()
    conn.close()

    print(f"\n{'─'*65}")
    print(f"✅ Fixed   : {fixed}/{len(MANUAL_COVERS)}")
    print(f"📊 Total DB Coverage: {covered}/{total} ({covered/total*100:.1f}%)")

    if still_missing:
        print(f"\n⚠️  Still missing ({len(still_missing)}):")
        for row in still_missing:
            print(f"   • {row[0]}")
    else:
        print(f"\n🎉 100% coverage achieved!")

    # Clean up missing_covers.txt
    missing_file = os.path.join(ROOT, "data", "missing_covers.txt")
    if os.path.exists(missing_file):
        os.remove(missing_file)
        print("🗑️  Cleaned up missing_covers.txt")


if __name__ == "__main__":
    apply_manual_covers()