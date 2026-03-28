import json
import re
from state.schema import EcommerceState
from tools.llm_config import groq_llm

CRITIC_PROMPT = """You are a quality validator for an AI recommendation system.

User Query: "{query}"
Budget Constraint: {budget}

Recommended Book:
- Title: {title}
- Price: ₹{price}
- Rating: {rating}/5

Recommendation Text:
"{recommendation}"

Validate strictly:
1. Budget: Is the price within the stated budget? (critical)
2. Relevance: Does the recommendation match what the user asked for?
3. Reasoning: Is the reasoning specific and useful — not vague?
4. Honesty: Does it mention at least one limitation?
5. Hallucination: Does it make any claims not supported by the data above?

Scoring guide:
- 0.9-1.0: Excellent, no issues
- 0.7-0.89: Good, minor issues
- 0.5-0.69: Acceptable but needs improvement
- Below 0.5: Retry needed

Respond in strict JSON only — no explanation, no markdown:
{{
  "score": <0.0 to 1.0>,
  "budget_satisfied": <true/false>,
  "is_relevant": <true/false>,
  "reasoning_clear": <true/false>,
  "issues": ["<issue1>", "<issue2>"],
  "feedback": "<one actionable sentence for improvement or 'Recommendation looks great'>",
  "verdict": "pass|retry"
}}"""


def critic_node(state: EcommerceState) -> dict:
    print(f"\n🧐 [CRITIC] Validating recommendation...")

    # Get recommended product details
    product_list = state["product_list"]
    best_id = state.get("recommended_product_id")
    product = next((p for p in product_list if p["id"] == best_id), product_list)

    prompt = CRITIC_PROMPT.format(
        query=state["user_query"],
        budget=f"₹{state['budget']}" if state.get("budget") else "No limit specified",
        title=product["title"],
        price=product["price"],
        rating=product["rating"],
        recommendation=state["final_answer"]
    )

    response = groq_llm.invoke(prompt)
    raw = response.content.strip()
    raw = re.sub(r"```(?:json)?", "", raw).strip()

    try:
        data = json.loads(raw)
        score    = float(data.get("score", 0.8))
        feedback = data.get("feedback", "Looks good.")
        issues   = data.get("issues", [])
        verdict  = data.get("verdict", "pass")
    except (json.JSONDecodeError, ValueError):
        score    = 0.8
        feedback = "Validation parsing failed — passing by default."
        issues   = []
        verdict  = "pass"

    retry_count = state.get("retry_count", 0) + 1

    print(f"  Score: {score:.2f} | Verdict: {verdict.upper()} | Retries: {retry_count-1}")
    if issues:
        print(f"  Issues: {', '.join(issues)}")
    print(f"  Feedback: {feedback}")

    return {
        "validation_score":    score,
        "validation_feedback": feedback,
        "retry_count":         retry_count,
        "current_node":        "critic"
    }
