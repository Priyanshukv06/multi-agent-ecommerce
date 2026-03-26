from langgraph.graph import StateGraph, END
from langgraph.graph import START
from langchain_nvidia_langgraph.graph import OptimizationConfig  # NVIDIA parallel boost
from state.schema import EcommerceState

# ── Node imports (will be filled Phase 3) ──────────────────────────────────
from agents.planner import planner_node
from agents.search import search_node
from agents.research import research_node
from agents.comparison import comparison_node
from agents.recommendation import recommendation_node
from agents.critic import critic_node
from agents.action import action_node

# ── Conditional routing functions ──────────────────────────────────────────

def route_after_planner(state: EcommerceState) -> str:
    """Planner decides which flow to enter."""
    intent = state["intent"]
    if intent == "recommendation":
        return "search"
    elif intent == "order":
        return "action"
    elif intent == "return":
        return "action"
    elif intent == "track":
        return "action"
    else:
        return "search"   # fallback

def route_after_critic(state: EcommerceState) -> str:
    """Critic decides: pass output OR loop back."""
    score = state["validation_score"]
    retry = state["retry_count"]
    if score >= 0.7 or retry >= 3:
        return "output"
    else:
        return "recommendation"   # retry loop

# ── Build the Graph ────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(EcommerceState)

    # Add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("search", search_node)
    graph.add_node("research", research_node)
    graph.add_node("comparison", comparison_node)
    graph.add_node("recommendation", recommendation_node)
    graph.add_node("critic", critic_node)
    graph.add_node("action", action_node)

    # Entry point
    graph.add_edge(START, "planner")

    # Planner → conditional branch
    graph.add_conditional_edges("planner", route_after_planner, {
        "search": "search",
        "action": "action",
    })

    # Recommendation pipeline
    graph.add_edge("search", "research")
    graph.add_edge("research", "comparison")
    graph.add_edge("comparison", "recommendation")
    graph.add_edge("recommendation", "critic")

    # Critic loop
    graph.add_conditional_edges("critic", route_after_critic, {
        "output": END,
        "recommendation": "recommendation",
    })

    # Action flow
    graph.add_edge("action", END)

    # Compile with NVIDIA parallel optimization
    return graph.compile(
        optimization=OptimizationConfig(enable_parallel=True)
    )

app = build_graph()
