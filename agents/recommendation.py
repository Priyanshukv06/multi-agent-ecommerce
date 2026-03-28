from state.schema import EcommerceState
from tools.llm_config import nvidia_llm
from tools.db_tool import get_product_by_id

RECOMMENDATION_PROMPT = """You are a helpful AI book advisor. A user needs your recommendation.

User Query: "{query}"
Budget: {budget}

Best Book Identified:
- Title: {title}
- Author: {author}
- Price: ₹{price}
- Rating: {rating}/5
- Why it won: {reasoning}

Key Strengths from Reviews:
{pros}

One Honest Limitation:
{cons}

Best For:
{use_cases}

Write a warm, helpful recommendation. Structure it as:
1. Direct recommendation (1 sentence)
2. Three specific reasons why this fits their needs (bullet points)
3. One honest limitation to set expectations
4. Encouraging closing line

Keep it under 180 words. Sound like a knowledgeable friend — not a robot or salesperson."""


def recommendation_node(state: EcommerceState) -> dict:
    print(f"\n✍️  [RECOMMENDATION] Generating recommendation...")

    comparison  = state["comparison_result"]
    best_id     = comparison["best_choice_id"]
    research_map = {r["product_id"]: r for r in state["research_data"]}
    research    = research_map.get(best_id, {})

    # Get full product details
    product = get_product_by_id(best_id)
    if not product:
        product = next((p for p in state["product_list"] if p["id"] == best_id),
                       state["product_list"])

    pros_text     = "\n".join([f"• {p}" for p in research.get("pros", [])[:3]])
    cons_text     = research.get("cons", ["Some advanced sections"])
    use_case_text = "\n".join([f"• {u}" for u in research.get("use_cases", [])[:2]])

    prompt = RECOMMENDATION_PROMPT.format(
        query=state["user_query"],
        budget=f"₹{state['budget']}" if state.get("budget") else "flexible",
        title=product["title"],
        author=product["author"],
        price=product["price"],
        rating=product["rating"],
        reasoning=comparison["reasoning"],
        pros=pros_text or "• Highly rated by readers\n• Practical approach",
        cons=cons_text,
        use_cases=use_case_text or "• Anyone learning the subject"
    )

    response = nvidia_llm.invoke(prompt)
    final_answer = response.content.strip()

    print(f"  ✅ Recommendation generated ({len(final_answer.split())} words)")
    print(f"  📖 Recommending: {product['title']}")

    return {
        "final_answer":            final_answer,
        "recommended_product_id":  best_id,
        "current_node":            "recommendation"
    }
