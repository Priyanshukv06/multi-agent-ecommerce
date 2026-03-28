import pytest
import uuid
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from memory.conversation_store import (
    save_turn, get_history, get_last_context,
    clear_session, format_history_for_prompt
)


class TestMemory:

    def setup_method(self):
        """Fresh session ID for every test."""
        self.session_id = f"test-{uuid.uuid4()}"

    def teardown_method(self):
        """Clean up after every test."""
        clear_session(self.session_id)

    def test_save_and_retrieve_turn(self):
        """Saved turn appears in history."""
        save_turn(
            session_id="test-session-memory",
            user_query="recommend a python book",
            assistant_response="I recommend Python Crash Course.",
            intent="recommendation",
            category="python",
            budget=800.0,
            product_id=3,
            order_id=None
        )
        history = get_history("test-session-memory")
        assert len(history) >= 2   # user + assistant
        roles = [h["role"] for h in history]
        assert "user"      in roles
        assert "assistant" in roles
        clear_session("test-session-memory")

    def test_history_in_chronological_order(self):
        """History returns turns in chronological order."""
        save_turn(self.session_id, "first query",  "first response",  "recommendation")
        save_turn(self.session_id, "second query", "second response", "order")
        history = get_history(self.session_id)
        contents = [h["content"] for h in history]
        assert contents.index("first query") < contents.index("second query")

    def test_get_last_context_returns_most_recent(self):
        """get_last_context returns most recent product_id and category."""
        save_turn(
            self.session_id, "old query", "old response",
            category="python", product_id=1
        )
        save_turn(
            self.session_id, "new query", "new response",
            category="deep learning", product_id=5
        )
        ctx = get_last_context(self.session_id)
        assert ctx["category"]   == "deep learning"
        assert ctx["product_id"] == 5

    def test_empty_session_returns_empty_history(self):
        """New session has no history."""
        history = get_history(f"empty-{uuid.uuid4()}")
        assert history == []

    def test_empty_session_context_has_none_values(self):
        """New session context has all None values."""
        ctx = get_last_context(f"empty-{uuid.uuid4()}")
        assert ctx["category"]   is None
        assert ctx["product_id"] is None
        assert ctx["order_id"]   is None

    def test_clear_session_removes_all_turns(self):
        """clear_session removes all data for that session."""
        save_turn(self.session_id, "query", "response", "recommendation")
        clear_session(self.session_id)
        history = get_history(self.session_id)
        assert history == []

    def test_format_history_for_prompt(self):
        """format_history_for_prompt returns readable string."""
        history = [
            {"role": "user",      "content": "I want a ML book"},
            {"role": "assistant", "content": "I recommend Hands-On ML"},
        ]
        result = format_history_for_prompt(history)
        assert "User"      in result
        assert "Assistant" in result
        assert "ML book"   in result

    def test_format_empty_history(self):
        """format_history_for_prompt handles empty history."""
        result = format_history_for_prompt([])
        assert result == "No previous conversation."

    def test_budget_persists_in_context(self):
        """Budget is retrievable from last context."""
        save_turn(
            self.session_id, "ml book under 1000", "response",
            budget=1000.0, category="machine learning"
        )
        ctx = get_last_context(self.session_id)
        assert ctx["budget"] == 1000.0
