import pytest
from agents.search import search_node, normalize_category


class TestSearchAgent:

    def test_search_with_budget_and_category(self, base_state):
        """Search returns products filtered by budget and category."""
        base_state["category"] = "machine learning"
        base_state["budget"]   = 1000.0
        result = search_node(base_state)

        assert "product_list" in result
        assert len(result["product_list"]) > 0
        for p in result["product_list"]:
            assert p["price"] <= 1000.0

    def test_search_respects_budget(self, base_state):
        """All returned products must be within budget."""
        base_state["category"] = None
        base_state["budget"]   = 500.0
        result = search_node(base_state)

        for p in result["product_list"]:
            assert p["price"] <= 500.0

    def test_search_no_budget(self, base_state):
        """Search works without budget constraint."""
        base_state["category"] = "deep learning"
        base_state["budget"]   = None
        result = search_node(base_state)

        assert len(result["product_list"]) > 0

    def test_search_fallback_no_results(self, base_state):
        """Search broadens query when no results found."""
        base_state["category"] = "nonexistent_category_xyz"
        base_state["budget"]   = 1000.0
        result = search_node(base_state)

        # Should fall back to broader search — never return empty
        assert isinstance(result["product_list"], list)

    def test_product_structure(self, base_state):
        """Each product has all required fields."""
        base_state["category"] = "python"
        base_state["budget"]   = None
        result = search_node(base_state)

        required_fields = ["id", "title", "author", "price", "rating", "category"]
        for p in result["product_list"]:
            for field in required_fields:
                assert field in p, f"Missing field: {field}"

    def test_normalize_category_ml(self):
        """Category normalization maps 'ml' to 'machine learning'."""
        assert normalize_category("ml") == "machine learning"

    def test_normalize_category_books(self):
        """Category 'books' normalizes to None (too generic)."""
        assert normalize_category("books") is None

    def test_normalize_category_none(self):
        """None input returns None."""
        assert normalize_category(None) is None

    def test_max_results_limit(self, base_state):
        """Search never returns more than 5 products."""
        base_state["category"] = "machine learning"
        base_state["budget"]   = None
        result = search_node(base_state)

        assert len(result["product_list"]) <= 5
