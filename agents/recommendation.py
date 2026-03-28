from state.schema import EcommerceState
from tools.llm_config import nvidia_llm
from tools.db_tool import get_product_by_id

RECOMMENDATION_PROMPT = """You are a warm, knowledgeable AI book advisor. 
Your goal: give the user a recommendation they will trust and act on.

User Query: "{query}"
Budget: {budget}
{retry_note}

━━━ BEST BOOK FOR THIS USER ━━━
Title:   {title}
Author:  {author}
Price:   ₹{price} (fits budget: {fits_budget})
Rating:  {rating}/5 ⭐
Level:   {difficulty}

Why it ranked #1 over {num_alternatives} other options:
{reasoning}

Key Strengths (from real reader reviews):
{pros}

Honest Limitation:
⚠️ {cons}

Best for people who:
{use_cases}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Write a recommendation response following this exact structure:

**My Recommendation: [Book Title]** (₹[price])

[2 sentences — directly answer why THIS book for THIS user's query]

**Why this book:**
• [Specific reason 1 tied to user's goal]
• [Specific reason 2 tied to user's goal]  
• [Specific reason 3 — practical benefit]

**One thing to know:** [Honest limitation in 1 sentence]

[1 encouraging closing sentence]

Rules:
- Under 160 words total
- Use the actual book title, author, price from the data above
- Never invent features or claims not in the data
- Sound like a helpful friend, not a product listing"""


def recommendation_node(state: EcommerceState) -> dict:
    print(f"\n✍️  [RECOMMENDATION] Generating recommendation...")

    comparison   = state["comparison_result"]
    best_id      = comparison["best_choice_id"]
    research_map = {r["product_id"]: r for r in state["research_data"]}
    research     = research_map.get(best_id, {})

    product = get_product_by_id(best_id)
    if not product:
        product = next(
            (p for p in state["product_list"] if p["id"] == best_id),
            state["product_list"][0]
        )

    # Check if this is a retry — include critic feedback
    retry_count = state.get("retry_count", 0)
    retry_note  = ""
    if retry_count > 0 and state.get("validation_feedback"):
        retry_note = f"⚠️  Previous attempt was flagged: '{state['validation_feedback']}'\nPlease specifically address this issue in your response.\n"
        print(f"  🔁 Retry #{retry_count} — addressing: {state['validation_feedback'][:60]}")

    # Budget check
    budget      = state.get("budget")
    fits_budget = "✅ Yes" if (not budget or product["price"] <= budget) else f"⚠️  Slightly over (₹{product['price']} vs ₹{budget})"

    pros_text     = "\n".join([f"• {p}" for p in research.get("pros", ["Highly rated"])[:3]])
    cons_list = research.get("cons", [])
    cons_text = cons_list[0] if cons_list else "Some sections may challenge beginners"

    use_case_text = "\n".join([f"• {u}" for u in research.get("use_cases", ["Self-learners"])[:2]])

    prompt = RECOMMENDATION_PROMPT.format(
        query=state["user_query"],
        budget=f"₹{budget}" if budget else "Flexible",
        retry_note=retry_note,
        title=product["title"],
        author=product["author"],
        price=product["price"],
        fits_budget=fits_budget,
        rating=product["rating"],
        difficulty=research.get("difficulty_level", "intermediate"),
        num_alternatives=len(state["product_list"]) - 1,
        reasoning=comparison["reasoning"],
        pros=pros_text,
        cons=cons_text,
        use_cases=use_case_text
    )

    response     = nvidia_llm.invoke(prompt)
    final_answer = response.content.strip()

    print(f"  ✅ Generated ({len(final_answer.split())} words) for: {product['title'][:45]}")

    return {
        "final_answer":            final_answer,
        "recommended_product_id":  best_id,
        "current_node":            "recommendation"
    }
