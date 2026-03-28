import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.db_tool import search_products, get_product_by_id, get_all_categories, get_price_range

def test_search_under_budget():
    results = search_products(category="machine learning", max_price=1000.0)
    print(f"\n📚 ML books under ₹1000: {len(results)} found")
    for b in results:
        print(f"  - {b['title']} | ₹{b['price']} | ⭐{b['rating']}")
    assert len(results) > 0

def test_categories():
    cats = get_all_categories()
    print(f"\n🏷️  Categories: {cats}")
    assert len(cats) > 0

def test_price_range():
    pr = get_price_range()
    print(f"\n💰 Price range: ₹{pr['min']} - ₹{pr['max']} | Avg: ₹{pr['avg']}")

def test_get_by_id():
    product = get_product_by_id(1)
    print(f"\n🔍 Product ID 1: {product['title']}")
    assert product is not None

if __name__ == "__main__":
    test_search_under_budget()
    test_categories()
    test_price_range()
    test_get_by_id()
    print("\n✅ All DB tests passed!")
