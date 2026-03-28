from langgraph.graph import StateGraph, END, START
from state.schema import EcommerceState
from agents.planner       import planner_node
from agents.search        import search_node
from agents.research      import research_node
from agents.comparison    import comparison_node
from agents.recommendation import recommendation_node
from agents.critic        import critic_node
from agents.action        import action_node

# ── Conditional Routing Functions ─────────────────────────────────────────

def route_after_planner(state: EcommerceState) -> str:
    intent = state.get("intent", "recommendation")
    if intent in ("order", "return", "track"):
        return "action"
    return "search"   # recommendation, compare, faq all go through search


def route_after_critic(state: EcommerceState) -> str:
    score       = state.get("validation_score", 0.8)
    retry_count = state.get("retry_count", 0)

    if score >= 0.7 or retry_count >= 3:
        if retry_count >= 3:
            print(f"  ⚠️  Max retries reached — forcing output")
        return END
    print(f"  🔁 Score {score:.2f} < 0.7 — retrying recommendation...")
    return "recommendation"


# ── Build Graph ───────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(EcommerceState)

    # Register nodes
    graph.add_node("planner",        planner_node)
    graph.add_node("search",         search_node)
    graph.add_node("research",       research_node)
    graph.add_node("comparison",     comparison_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("critic",         critic_node)
    graph.add_node("action",         action_node)

    # Entry
    graph.add_edge(START, "planner")

    # Planner → branch
    graph.add_conditional_edges(
        "planner",
        route_after_planner,
        {"search": "search", "action": "action"}
    )

    # Recommendation pipeline
    graph.add_edge("search",      "research")
    graph.add_edge("research",    "comparison")
    graph.add_edge("comparison",  "recommendation")
    graph.add_edge("recommendation", "critic")

    # Critic → pass or loop
    graph.add_conditional_edges(
        "critic",
        route_after_critic,
        {END: END, "recommendation": "recommendation"}
    )

    # Action → end
    graph.add_edge("action", END)

    return graph.compile()


app = build_graph()
