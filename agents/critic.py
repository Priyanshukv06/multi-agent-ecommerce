import json
import re
from state.schema import EcommerceState
from tools.llm_config import groq_llm

CRITIC_PROMPT = """You are a strict quality validator for an AI book recommendation system.
Your job is to catch bad recommendations BEFORE the user sees them.

━━━ CONTEXT ━━━
User Query:  "{query}"
User Budget: {budget}
Retry Count: {retry_count} (max 3 before force-pass)

━━━ RECOMMENDED BOOK ━━━
Title:  {title}
Author: {author}
Price:  ₹{price}
Rating: {rating}/5

━━━ RECOMMENDATION TEXT ━━━
{recommendation}

━━━ VALIDATE THESE 5 DIMENSIONS ━━━

1. BUDGET CHECK (critical): 
   - If budget was stated, is price ≤ budget? 
   - Flag if price exceeds budget by more than ₹50

2. RELEVANCE CHECK:
   - Does the recommendation actually match the user's query topic?
   - Is the book in the right category?

3. REASONING CHECK:
   - Are the reasons specific (mentions actual book features)?
   - Or vague ("great book", "highly recommended")?

4. HONESTY CHECK:
   - Does it mention at least one limitation or caveat?
   - Recommendations with zero cons are suspicious

5. HALLUCINATION CHECK:
   - Does the text mention price/rating/author correctly?
   - Any claims that contradict the book data above?

━━━ SCORING ━━━
Start at 1.0, deduct:
- Budget violated by > ₹50: -0.4
- Wrong category/irrelevant: -0.3
- Vague reasoning only: -0.2
- No limitation mentioned: -0.1
- Any hallucinated fact: -0.3

Respond in strict JSON only:
{{
  "score": <0.0 to 1.0>,
  "budget_satisfied": <true/false>,
  "is_relevant": <true/false>,
  "reasoning_clear": <true/false>,
  "has_limitation": <true/false>,
  "hallucination_detected": <true/false>,
  "issues": ["<specific issue>", "<specific issue>"],
  "feedback": "<one specific actionable sentence — what to fix>",
  "verdict": "pass|retry"
}}"""


def critic_node(state: EcommerceState) -> dict:
    print(f"\n🧐 [CRITIC] Validating recommendation (attempt {state.get('retry_count', 0) + 1})...")

    best_id  = state.get("recommended_product_id")
    product  = next(
        (p for p in state["product_list"] if p["id"] == best_id),
        state["product_list"][0]
    )

    prompt = CRITIC_PROMPT.format(
        query=state["user_query"],
        budget=f"₹{state['budget']}" if state.get("budget") else "Not specified",
        retry_count=state.get("retry_count", 0),
        title=product["title"],
        author=product["author"],
        price=product["price"],
        rating=product["rating"],
        recommendation=state["final_answer"]
    )

    response = groq_llm.invoke(prompt)
    raw      = re.sub(r"```(?:json)?", "", response.content.strip()).strip()

    try:
        data     = json.loads(raw)
        score    = round(float(data.get("score", 0.8)), 2)
        feedback = data.get("feedback", "Looks good.")
        issues   = data.get("issues", [])
        verdict  = data.get("verdict", "pass")

        print(f"  Score: {score:.2f} | Verdict: {verdict.upper()}")
        if issues:
            print(f"  Issues found: {' | '.join(issues)}")
        print(f"  Feedback: {feedback[:80]}")

    except (json.JSONDecodeError, ValueError):
        score    = 0.8
        feedback = "Validation parsing failed — passing by default."
        issues   = []
        verdict  = "pass"
        print(f"  ⚠️  Critic parse failed — defaulting to score 0.8 / pass")

    retry_count = state.get("retry_count", 0) + 1

    return {
        "validation_score":    score,
        "validation_feedback": feedback,
        "retry_count":         retry_count,
        "current_node":        "critic"
    }
