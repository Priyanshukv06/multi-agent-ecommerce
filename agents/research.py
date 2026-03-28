import json
import re
from typing import List
from state.schema import EcommerceState, ResearchData
from tools.llm_config import nvidia_fast
from tools.json_utils import extract_json

RESEARCH_PROMPT = """You are an expert book analyst. Analyze these customer reviews carefully.

Book: "{title}" by {author}
Price: Rs.{price} | Rating: {rating}/5
Description: {description}

Customer Reviews:
{reviews}

Extract deep insights. Be specific — avoid generic statements.

Respond in strict JSON only — no markdown, no explanation outside the JSON block:
{{
  "product_id": {product_id},
  "title": "{safe_title}",
  "pros": ["<specific strength 1>", "<specific strength 2>", "<specific strength 3>"],
  "cons": ["<honest limitation 1>", "<honest limitation 2>"],
  "difficulty_level": "beginner",
  "use_cases": ["<who should read this 1>", "<who should read this 2>"],
  "summary": "<2 sentences about what makes this book unique and who it is best for>"
}}

Replace difficulty_level value with one of: beginner, intermediate, advanced"""


def sanitize(text: str) -> str:
    """Remove characters that break JSON inside prompts."""
    return (
        text.replace('"', "'")
            .replace('\\', '')
            .replace('\n', ' ')
            .replace('{', '(')
            .replace('}', ')')
            .strip()
    )


def research_single_product(product: dict) -> ResearchData:
    """Research one product — called sequentially."""
    reviews_text = "\n".join([
        f"  {i+1}. {sanitize(r)}"
        for i, r in enumerate(product["reviews"])
    ])

    prompt = RESEARCH_PROMPT.format(
        title=sanitize(product["title"]),
        safe_title=sanitize(product["title"]),
        author=sanitize(product["author"]),
        price=product["price"],
        rating=product["rating"],
        description=sanitize(product["description"]),
        reviews=reviews_text,
        product_id=product["id"]
    )

    try:
        response = nvidia_fast.invoke(prompt)
        data     = extract_json(response.content)

        if not data:
            raise ValueError("Empty JSON extracted")

        return ResearchData(
            product_id=product["id"],
            title=product["title"],
            pros=data.get("pros", [])[:3],
            cons=data.get("cons", [])[:2],
            difficulty_level=data.get("difficulty_level", "intermediate"),
            use_cases=data.get("use_cases", [])[:2],
            summary=data.get("summary", product["description"])
        )

    except Exception as e:
        print(f"     ⚠️  Fallback used ({str(e)[:50]})")
        return ResearchData(
            product_id=product["id"],
            title=product["title"],
            pros=["Highly rated by readers", "Covers topic thoroughly", "Practical approach"],
            cons=["May not suit all learning styles", "Pacing varies by reader"],
            difficulty_level="intermediate",
            use_cases=["Anyone learning the subject", "Self-paced learners"],
            summary=product["description"]
        )


def research_node(state: EcommerceState) -> dict:
    """
    Sequential research node — reliable on free API tiers.
    
    NOTE: Parallel version using LangGraph Send API is architecturally
    superior and implemented in fan_out_research() below.
    Switch to parallel when using paid API tiers with higher rate limits.
    """
    print(f"\n📖 [RESEARCH] Analyzing {len(state['product_list'])} products...")

    results = []
    for product in state["product_list"]:
        print(f"  🔎 {product['title'][:45]}...")
        result = research_single_product(product)
        results.append(result)
        print(f"     ✅ {result['difficulty_level']} | {len(result['pros'])} pros | {len(result['cons'])} cons")

    print(f"  ✅ Research complete for {len(results)} books")
    return {
        "research_data": results,
        "current_node":  "research"
    }


# ── Parallel version — kept for Phase 4 upgrade on paid API tier ────────────
# Uncomment and wire in workflow.py when NVIDIA rate limits are not an issue

# from langgraph.types import Send
#
# def research_single_node(product: dict) -> dict:
#     result = research_single_product(product)
#     return {"research_data": [result]}
#
# def fan_out_research(state: EcommerceState):
#     print(f"\n📖 [RESEARCH] Launching parallel research for {len(state['product_list'])} books...")
#     return [Send("research_single", product) for product in state["product_list"]]
