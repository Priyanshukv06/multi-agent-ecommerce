import pytest
from agents.research import research_node, research_single_product


class TestResearchAgent:

    def test_research_returns_all_products(self, base_state, mock_products):
        """Research produces one result per product."""
        base_state["product_list"] = mock_products
        result = research_node(base_state)

        assert len(result["research_data"]) == len(mock_products)

    def test_research_data_structure(self, base_state, mock_products):
        """Each research result has required fields."""
        base_state["product_list"] = mock_products[:1]
        result = research_node(base_state)

        required = ["product_id", "title", "pros", "cons",
                    "difficulty_level", "use_cases", "summary"]
        for r in result["research_data"]:
            for field in required:
                assert field in r, f"Missing field: {field}"

    def test_difficulty_level_valid(self, base_state, mock_products):
        """Difficulty level is always one of the valid options."""
        base_state["product_list"] = mock_products[:2]
        result = research_node(base_state)

        valid_levels = {"beginner", "intermediate", "advanced"}
        for r in result["research_data"]:
            assert r["difficulty_level"] in valid_levels

    def test_pros_list_not_empty(self, base_state, mock_products):
        """Each book has at least one pro extracted."""
        base_state["product_list"] = mock_products[:1]
        result = research_node(base_state)

        for r in result["research_data"]:
            assert isinstance(r["pros"], list)
            assert len(r["pros"]) > 0

    def test_product_id_matches(self, base_state, mock_products):
        """Research result product_id matches input product id."""
        base_state["product_list"] = mock_products
        result = research_node(base_state)

        input_ids  = {p["id"] for p in mock_products}
        result_ids = {r["product_id"] for r in result["research_data"]}
        assert result_ids == input_ids

    def test_single_product_research(self, mock_products):
        """research_single_product returns valid ResearchData."""
        product = mock_products[0]
        result  = research_single_product(product)

        assert result["product_id"] == product["id"]
        assert result["title"] == product["title"]
        assert isinstance(result["pros"], list)
        assert isinstance(result["cons"], list)

    def test_fallback_on_bad_product(self):
        """Research handles missing reviews gracefully with fallback."""
        bad_product = {
            "id": 999, "title": "Test Book", "author": "Test",
            "price": 500.0, "rating": 4.0, "category": "test",
            "description": "Test description", "reviews": []
        }
        result = research_single_product(bad_product)

        assert result["product_id"] == 999
        assert isinstance(result["pros"], list)
