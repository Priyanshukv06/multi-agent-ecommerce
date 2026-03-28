import pytest
from agents.planner import planner_node


class TestPlannerAgent:

    def test_recommendation_intent(self, base_state):
        """Planner correctly identifies recommendation intent."""
        base_state["user_query"] = "I want a good book to learn machine learning under ₹1000"
        result = planner_node(base_state)

        assert result["intent"] == "recommendation"
        assert result["budget"] == 1000.0
        assert "machine learning" in result["category"].lower()
        assert "search" in result["plan"]

    def test_budget_extraction(self, base_state):
        """Planner correctly extracts budget from query."""
        base_state["user_query"] = "suggest a python book under ₹500"
        result = planner_node(base_state)

        assert result["budget"] is not None
        assert result["budget"] <= 500.0

    def test_order_intent(self, base_state):
        """Planner identifies order intent."""
        base_state["user_query"] = "buy this book"
        result = planner_node(base_state)

        assert result["intent"] == "order"
        assert result["plan"] == ["action"]

    def test_track_intent(self, base_state):
        """Planner identifies tracking intent."""
        base_state["user_query"] = "Where is my order ORD-00001"
        result = planner_node(base_state)

        assert result["intent"] == "track"
        assert result["plan"] == ["action"]

    def test_return_intent(self, base_state):
        """Planner identifies return intent."""
        base_state["user_query"] = "I want to return my last order"
        result = planner_node(base_state)

        assert result["intent"] == "return"

    def test_compare_intent(self, base_state):
        """Planner identifies compare intent."""
        base_state["user_query"] = "Compare deep learning books"
        result = planner_node(base_state)

        assert result["intent"] in ("compare", "recommendation")

    def test_no_budget_query(self, base_state):
        """Planner handles query with no budget mentioned."""
        base_state["user_query"] = "best python programming book"
        result = planner_node(base_state)

        assert result["intent"] == "recommendation"
        assert result["budget"] is None

    def test_retry_count_initialized(self, base_state):
        """Planner always initializes retry_count to 0."""
        base_state["user_query"] = "recommend a data science book"
        result = planner_node(base_state)

        assert result["retry_count"] == 0

    def test_plan_not_empty(self, base_state):
        """Planner always returns a non-empty plan."""
        base_state["user_query"] = "something random"
        result = planner_node(base_state)

        assert isinstance(result["plan"], list)
        assert len(result["plan"]) > 0
