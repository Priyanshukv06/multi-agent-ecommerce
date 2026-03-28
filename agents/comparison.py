from state.schema import EcommerceState, ComparisonResult
from tools.llm_config import groq_llm


def flatten_research(research_data: list) -> list:
    flat = []
    for item in research_data:
        if isinstance(item, list):
            flat.extend(item)
        elif isinstance(item, dict):
            flat.append(item)
    return flat


def score_products(product_list: list, research_data: list, user_query: str) -> list:
    """Pure Python scoring — no LLM, never fails, never truncates."""
    research_data = flatten_research(research_data)
    research_map  = {r["product_id"]: r for r in research_data if isinstance(r, dict)}
    query_lower   = user_query.lower()

    scored = []
    for p in product_list:
        r          = research_map.get(p["id"], {})
        difficulty = r.get("difficulty_level", "intermediate")

        # ── Price value score ─────────────────────────────
        price = p["price"]
        if price <= 500:   price_score = 10
        elif price <= 750: price_score = 8
        elif price <= 900: price_score = 7
        elif price <= 1000: price_score = 6
        else:              price_score = 4

        # ── Beginner friendliness score ───────────────────
        diff_map       = {"beginner": 9, "intermediate": 6, "advanced": 3}
        beginner_score = diff_map.get(difficulty, 6)

        # ── Content depth score ───────────────────────────
        num_pros    = len(r.get("pros", []))
        desc_length = len(p.get("description", ""))
        depth_score = min(10, (num_pros * 2) + (desc_length // 60))

        # ── Rating score ──────────────────────────────────
        rating_score = round(p["rating"] * 2)

        # ── Query-based weight adjustment ─────────────────
        if any(w in query_lower for w in ["beginner", "start", "learn", "basic", "new to"]):
            beginner_score = min(10, int(beginner_score * 1.5))
        if any(w in query_lower for w in ["deep", "advanced", "research", "expert", "rigorous"]):
            depth_score = min(10, int(depth_score * 1.5))

        total = price_score + beginner_score + depth_score + rating_score

        scored.append({
            "rank":             0,
            "product_id":       p["id"],
            "title":            p["title"],
            "price_value":      price_score,
            "beginner_friendly": beginner_score,
            "content_depth":    depth_score,
            "rating_score":     rating_score,
            "total_score":      total,
        })

    # Sort and assign ranks
    scored.sort(key=lambda x: x["total_score"], reverse=True)
    for i, s in enumerate(scored):
        s["rank"] = i + 1

    return scored


def get_reasoning(winner: dict, winner_product: dict, winner_research: dict, query: str) -> str:
    """Ask LLM for 2-sentence reasoning only — tiny output, never truncates."""
    top_pro = winner_research.get("pros", ["highly rated by readers"])[0]

    prompt = (
        f'In exactly 2 sentences, explain why "{winner["title"]}" is the best choice '
        f'for someone who asked: "{query}"\n\n'
        f'Facts: Price Rs.{winner_product["price"]} | '
        f'Rating {winner_product["rating"]}/5 | '
        f'Level: {winner_research.get("difficulty_level", "intermediate")} | '
        f'Top strength: {top_pro}\n\n'
        f'Two sentences only. No bullet points. No markdown.'
    )

    try:
        response = groq_llm.invoke(prompt)
        return response.content.strip()
    except Exception:
        return (
            f"{winner['title']} offers the best combination of price, "
            f"rating, and content depth for this query."
        )


def comparison_node(state: EcommerceState) -> dict:
    print(f"\n⚖️  [COMPARISON] Comparing {len(state['product_list'])} books...")

    # ── Step 1: Score in pure Python ──────────────────────────────────────────
    scored = score_products(
        state["product_list"],
        state["research_data"],
        state["user_query"]
    )

    winner         = scored[0]
    winner_product = next(
        (p for p in state["product_list"] if p["id"] == winner["product_id"]),
        state["product_list"][0]
    )

    research_data = flatten_research(state["research_data"])
    research_map  = {r["product_id"]: r for r in research_data if isinstance(r, dict)}
    winner_research = research_map.get(winner["product_id"], {})

    # ── Step 2: LLM for reasoning only (2 sentences max) ─────────────────────
    reasoning = get_reasoning(winner, winner_product, winner_research, state["user_query"])

    # ── Step 3: Build result ──────────────────────────────────────────────────
    result = ComparisonResult(
        ranked_products=scored,
        best_choice_id=winner["product_id"],
        scoring_table=scored,
        reasoning=reasoning
    )

    scores_display = [
        f"{s['title'][:20]}={s['total_score']}"
        for s in scored[:3]
    ]
    print(f"  ✅ Winner: {winner['title'][:50]}")
    print(f"  📊 Scores: {scores_display}")

    return {
        "comparison_result": result,
        "current_node":      "comparison"
    }
