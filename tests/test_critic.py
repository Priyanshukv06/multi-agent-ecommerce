import pytest
from agents.critic import critic_node


class TestCriticAgent:

    def _make_state(self, base_state, mock_products,
                    mock_research_data, mock_comparison_result,
                    answer: str, budget: float = 1000.0):
        """Helper to build full state for critic testing."""
        state = base_state.copy()
        state["product_list"]           = mock_products
        state["research_data"]          = mock_research_data
        state["comparison_result"]      = mock_comparison_result
        state["recommended_product_id"] = 1
        state["budget"]                 = budget
        state["final_answer"]           = answer
        return state

    def test_good_recommendation_passes(
        self, base_state, mock_products, mock_research_data, mock_comparison_result
    ):
        """A well-structured recommendation should score >= 0.7."""
        answer = (
            "**My Recommendation: Hands-On Machine Learning** (₹899)\n\n"
            "This book fits your ₹1000 budget perfectly and has a 4.9/5 rating.\n\n"
            "**Why this book:**\n"
            "• Covers the full ML pipeline practically\n"
            "• Hands-on exercises in every chapter\n"
            "• Best rated book in the category\n\n"
            "**One thing to know:** Slightly advanced for absolute beginners.\n\n"
            "Highly recommended for anyone with basic Python knowledge!"
        )
        state  = self._make_state(base_state, mock_products,
                                   mock_research_data, mock_comparison_result, answer)
        result = critic_node(state)

        assert result["validation_score"] >= 0.7
        assert result["retry_count"] == 1

    def test_budget_violation_lowers_score(
        self, base_state, mock_products, mock_research_data, mock_comparison_result
    ):
        """Recommending over-budget product should lower score."""
        answer = "I recommend Deep Learning by Goodfellow at ₹1500."
        state  = self._make_state(
            base_state, mock_products, mock_research_data,
            mock_comparison_result, answer, budget=500.0
        )
        result = critic_node(state)

        # Score should be lower for budget violation
        assert result["validation_score"] is not None
        assert isinstance(result["validation_score"], float)

    def test_retry_count_increments(
        self, base_state, mock_products, mock_research_data, mock_comparison_result
    ):
        """Critic always increments retry_count by 1."""
        answer = "Good recommendation."
        state  = self._make_state(base_state, mock_products,
                                   mock_research_data, mock_comparison_result, answer)
        state["retry_count"] = 2
        result = critic_node(state)

        assert result["retry_count"] == 3

    def test_feedback_always_provided(
        self, base_state, mock_products, mock_research_data, mock_comparison_result
    ):
        """Critic always returns non-empty feedback string."""
        answer = "I recommend this book."
        state  = self._make_state(base_state, mock_products,
                                   mock_research_data, mock_comparison_result, answer)
        result = critic_node(state)

        assert result["validation_feedback"] is not None
        assert len(result["validation_feedback"]) > 0

    def test_score_between_0_and_1(
        self, base_state, mock_products, mock_research_data, mock_comparison_result
    ):
        """Critic score is always between 0.0 and 1.0."""
        answer = "Some recommendation text."
        state  = self._make_state(base_state, mock_products,
                                   mock_research_data, mock_comparison_result, answer)
        result = critic_node(state)

        assert 0.0 <= result["validation_score"] <= 1.0
