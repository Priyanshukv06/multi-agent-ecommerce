import os
from dotenv import load_dotenv
load_dotenv()

os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_API_KEY"]    = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"]    = os.getenv("LANGCHAIN_PROJECT", "multi-agent-ecommerce")

from graph.workflow import app
from state.schema   import EcommerceState


def run_agent(query: str, recommended_product_id: int = None) -> dict:
    print("\n" + "=" * 65)
    print(f"👤 USER: {query}")
    print("=" * 65)

    initial_state: EcommerceState = {
        "user_query":             query,
        "conversation_history":   [],
        "intent":                 "",
        "plan":                   [],
        "budget":                 None,
        "category":               None,
        "product_list":           [],
        "research_data":          [],
        "comparison_result":      None,
        "final_answer":           "",
        "recommended_product_id": recommended_product_id,
        "validation_score":       0.0,
        "validation_feedback":    None,
        "retry_count":            0,
        "order_status":           None,
        "order_id":               None,
        "error":                  None,
        "current_node":           "start"
    }

    final_state = app.invoke(initial_state)

    print("\n" + "=" * 65)
    print("🤖 ASSISTANT:")
    print("=" * 65)
    print(final_state["final_answer"])
    print("=" * 65)

    return final_state


if __name__ == "__main__":
    # ── Phase 3+4 tests ──────────────────────────────────────────────────────
    run_agent("I want a good book to learn machine learning under ₹1000")
    run_agent("Compare deep learning books")

    # ── Phase 5 tests ────────────────────────────────────────────────────────
    # Test order placement (product_id=1 = Hands-On ML)
    state = run_agent("Buy it", recommended_product_id=1)
    placed_order_id = state.get("order_id", "ORD-00001")

    # Test tracking with real order ID from above
    run_agent(f"Where is my order {placed_order_id}")

    # Test show all orders
    run_agent("Show my orders")

    # Test return flow
    run_agent(f"Return my order {placed_order_id}")

    # Test track after return
    run_agent(f"Track order {placed_order_id}")
