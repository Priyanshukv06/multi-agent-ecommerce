from state.schema import EcommerceState
from tools.db_tool import search_products

# Category keyword normalization map
CATEGORY_MAP = {
    "ml":                    "machine learning",
    "machine learning":      "machine learning",
    "deep learning":         "deep learning",
    "neural":                "deep learning",
    "nlp":                   "nlp",
    "natural language":      "nlp",
    "python":                "python",
    "data science":          "data science",
    "data":                  "data science",
    "math":                  "mathematics",
    "mathematics":           "mathematics",
    "rl":                    "reinforcement learning",
    "reinforcement":         "reinforcement learning",
    "software":              "software engineering",
    "books":                 None,   # too generic — search all categories
}


def normalize_category(raw: str | None) -> str | None:
    if not raw:
        return None
    raw_lower = raw.lower().strip()
    for key, value in CATEGORY_MAP.items():
        if key in raw_lower:
            return value
    return raw_lower   # return as-is if no mapping found


def search_node(state: EcommerceState) -> dict:
    print(f"\n🔍 [SEARCH] Searching products...")

    category = normalize_category(state.get("category"))
    budget   = state.get("budget")

    products = search_products(
        category=category,
        max_price=budget,
        min_rating=4.0,
        limit=5
    )

    # Fallback: if no results, broaden search (remove category filter)
    if not products and category:
        print(f"  ⚠️  No results for '{category}', broadening search...")
        products = search_products(
            max_price=budget,
            min_rating=4.0,
            limit=5
        )

    # Final fallback: remove budget filter too
    if not products:
        print(f"  ⚠️  No results with budget ₹{budget}, removing budget filter...")
        products = search_products(
            category=category,
            min_rating=4.0,
            limit=5
        )

    print(f"  ✅ Found {len(products)} products")
    for p in products:
        print(f"     - {p['title'][:50]} | ₹{p['price']} | ⭐{p['rating']}")

    return {
        "product_list": products,
        "current_node": "search"
    }
