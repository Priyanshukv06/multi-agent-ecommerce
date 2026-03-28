import json
import re
from state.schema import EcommerceState, ComparisonResult
from tools.llm_config import nvidia_fast

COMPARISON_PROMPT = """You are comparing books to find the best match for a user.

User Query: "{query}"
Budget: {budget}
Category: {category}

Books to compare:
{books_summary}

Score each book (1-10) on these criteria:
- price_value: how good is the price for what you get?
- beginner_friendly: how accessible is it for newcomers?
- content_depth: how comprehensive and thorough is the content?
- rating_score: based on the actual rating out of 5

Rank them best to worst and pick one winner.

Respond in strict JSON only — no explanation, no markdown:
{{
  "ranked": [
    {{
      "rank": 1,
      "product_id": <id>,
      "title": "<title>",
      "price_value": <1-10>,
      "beginner_friendly": <1-10>,
      "content_depth": <1-10>,
      "rating_score": <1-10>,
      "total_score": <sum>
    }}
  ],
  "best_choice_id": <product_id of rank 1>,
  "best_choice_title": "<title>",
  "reasoning": "<2 specific sentences explaining why this book wins>"
}}"""


def build_books_summary(product_list, research_data) -> str:
    lines = []
    research_map = {r["product_id"]: r for r in research_data}

    for p in product_list:
        research = research_map.get(p["id"], {})
        pros = ", ".join(research.get("pros", [])[:2])
        cons = ", ".join(research.get("cons", [])[:1])
        difficulty = research.get("difficulty_level", "intermediate")

        lines.append(
            f"ID:{p['id']} | {p['title']} by {p['author']}\n"
            f"  Price: ₹{p['price']} | Rating: {p['rating']}/5 | Level: {difficulty}\n"
            f"  Pros: {pros}\n"
            f"  Cons: {cons}"
        )
    return "\n\n".join(lines)


def comparison_node(state: EcommerceState) -> dict:
    print(f"\n⚖️  [COMPARISON] Comparing {len(state['product_list'])} books...")

    books_summary = build_books_summary(
        state["product_list"],
        state["research_data"]
    )

    prompt = COMPARISON_PROMPT.format(
        query=state["user_query"],
        budget=f"₹{state['budget']}" if state.get("budget") else "No limit",
        category=state.get("category") or "general",
        books_summary=books_summary
    )

    response = nvidia_fast.invoke(prompt)
    raw = response.content.strip()
    raw = re.sub(r"```(?:json)?", "", raw).strip()

    try:
        data = json.loads(raw)
        result = ComparisonResult(
            ranked_products=data.get("ranked", []),
            best_choice_id=data.get("best_choice_id", state["product_list"][0]["id"]),
            scoring_table=data.get("ranked", []),
            reasoning=data.get("reasoning", "Best overall match for the user query.")
        )
        print(f"  ✅ Winner: {data.get('best_choice_title', 'N/A')}")
        print(f"     Reason: {data.get('reasoning', '')[:80]}...")
    except json.JSONDecodeError:
        # Safe fallback — pick highest rated
        best = max(state["product_list"], key=lambda x: x["rating"])
        result = ComparisonResult(
            ranked_products=[],
            best_choice_id=best["id"],
            scoring_table=[],
            reasoning=f"{best['title']} has the highest rating at {best['rating']}/5."
        )
        print(f"  ⚠️  JSON parse failed — fallback to highest rated: {best['title']}")

    return {
        "comparison_result": result,
        "current_node": "comparison"
    }
