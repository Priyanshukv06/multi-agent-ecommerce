import os
from dotenv import load_dotenv
load_dotenv()

# LangSmith tracing (free — shows every agent step)
os.environ["LANGCHAIN_TRACING_V2"]  = os.getenv("LANGCHAIN_TRACING_V2", "false")
os.environ["LANGCHAIN_API_KEY"]     = os.getenv("LANGCHAIN_API_KEY", "")
os.environ["LANGCHAIN_PROJECT"]     = os.getenv("LANGCHAIN_PROJECT", "multi-agent-ecommerce")

from graph.workflow import app
from state.schema   import EcommerceState


def run_agent(query: str):
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
        "recommended_product_id": None,
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
    # Test queries — run all three to verify full pipeline
    test_queries = [
        "I want a good book to learn machine learning under ₹1000",
        "Compare deep learning books",
        "Where is my order ORD-00001",
    ]

    for query in test_queries:
        run_agent(query)
        print("\n")
