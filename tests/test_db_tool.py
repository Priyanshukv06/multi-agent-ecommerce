import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.db_tool import (
    search_products, get_product_by_id, place_order,
    get_order, get_user_orders, initiate_return,
    get_all_categories, get_price_range
)


class TestDBTool:

    def test_search_returns_results(self):
        results = search_products(category="machine learning", max_price=1000.0)
        assert len(results) > 0

    def test_search_budget_filter(self):
        results = search_products(max_price=500.0)
        for r in results:
            assert r["price"] <= 500.0

    def test_get_product_by_id(self):
        product = get_product_by_id(1)
        assert product is not None
        assert product["id"] == 1
        assert "title" in product

    def test_get_nonexistent_product(self):
        product = get_product_by_id(9999)
        assert product is None

    def test_place_order_returns_order_id(self):
        order_id = place_order(product_id=1, user_id="test_user")
        assert order_id.startswith("ORD-")
        assert len(order_id) == 9   # ORD-XXXXX

    def test_get_order_after_placing(self):
        order_id = place_order(product_id=1, user_id="test_user")
        order    = get_order(order_id)
        assert order is not None
        assert order["order_id"] == order_id
        assert order["title"] is not None

    def test_get_user_orders(self):
        place_order(product_id=1, user_id="test_user_2")
        orders = get_user_orders("test_user_2")
        assert len(orders) > 0
        assert "order_id" in orders[0]

    def test_initiate_return_valid_order(self):
        order_id  = place_order(product_id=2, user_id="return_test_user")
        return_id = initiate_return(order_id, "Not needed", "return_test_user")
        assert return_id is not None
        assert return_id != "EXPIRED"
        assert return_id.startswith("RET-")

    def test_initiate_return_nonexistent_order(self):
        result = initiate_return("ORD-99999", "reason", "test_user")
        assert result is None

    def test_get_all_categories(self):
        cats = get_all_categories()
        assert len(cats) > 0
        assert "machine learning" in cats

    def test_price_range(self):
        pr = get_price_range()
        assert pr["min"] > 0
        assert pr["max"] >= pr["min"]
        assert pr["avg"] > 0

    def test_search_no_filters(self):
        results = search_products()
        assert len(results) > 0

    def test_product_has_reviews(self):
        product = get_product_by_id(1)
        assert isinstance(product["reviews"], list)
        assert len(product["reviews"]) > 0
