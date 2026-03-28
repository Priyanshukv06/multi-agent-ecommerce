import os
import uuid
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_API_KEY"]    = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"]    = os.getenv("LANGCHAIN_PROJECT", "multi-agent-ecommerce")

from graph.workflow import app
from state.schema   import EcommerceState
from memory.conversation_store import (
    save_turn, get_history, get_last_context, clear_session
)


def run_agent(
    query:       str,
    session_id:  str,
    recommended_product_id: int = None
) -> dict:
    print("\n" + "=" * 65)
    print(f"👤 USER: {query}")
    print("=" * 65)

    # ── Load history from memory ─────────────────────────────────────────────
    history      = get_history(session_id)
    last_context = get_last_context(session_id)

    # Inherit recommended_product_id from memory if not provided
    if not recommended_product_id:
        recommended_product_id = last_context.get("product_id")

    initial_state: EcommerceState = {
        "session_id":             session_id,
        "user_query":             query,
        "conversation_history":   history,
        "intent":                 "",
        "plan":                   [],
        "budget":                 last_context.get("budget"),
        "category":               last_context.get("category"),
        "product_list":           [],
        "research_data":          [],
        "comparison_result":      None,
        "final_answer":           "",
        "recommended_product_id": recommended_product_id,
        "validation_score":       0.0,
        "validation_feedback":    None,
        "retry_count":            0,
        "order_status":           None,
        "order_id":               last_context.get("order_id"),
        "error":                  None,
        "current_node":           "start"
    }

    final_state = app.invoke(initial_state)

    # ── Save turn to memory ──────────────────────────────────────────────────
    save_turn(
        session_id=  session_id,
        user_query=  query,
        assistant_response= final_state["final_answer"],
        intent=      final_state.get("intent"),
        category=    final_state.get("category"),
        budget=      final_state.get("budget"),
        product_id=  final_state.get("recommended_product_id"),
        order_id=    final_state.get("order_id"),
    )

    print("\n" + "=" * 65)
    print("🤖 ASSISTANT:")
    print("=" * 65)
    print(final_state["final_answer"])
    print("=" * 65)

    return final_state


if __name__ == "__main__":
    # ── Same session — tests memory continuity ───────────────────────────────
    session = str(uuid.uuid4())
    print(f"\n🔑 Session ID: {session}\n")

    # Turn 1 — recommendation
    run_agent(
        "I want a good book to learn machine learning under ₹1000",
        session_id=session
    )

    # Turn 2 — "buy it" — should remember product from Turn 1
    run_agent(
        "buy it",
        session_id=session
    )

    # Turn 3 — track — should remember order from Turn 2
    run_agent(
        "where is my order",
        session_id=session
    )

    # Turn 4 — new topic, no budget — should NOT inherit ML budget
    run_agent(
        "Compare deep learning books",
        session_id=session
    )

    # Turn 5 — return — should remember last order
    run_agent(
        "return my last order",
        session_id=session
    )
