import json
import re
from state.schema import EcommerceState, ResearchData
from tools.llm_config import nvidia_fast

RESEARCH_PROMPT = """Analyze these reviews for the book "{title}" by {author} (₹{price}, ⭐{rating}/5).

Book description: {description}

Customer reviews:
{reviews}

Extract structured insights in strict JSON only — no explanation, no markdown:
{{
  "product_id": {product_id},
  "title": "{title}",
  "pros": ["<specific pro 1>", "<specific pro 2>", "<specific pro 3>"],
  "cons": ["<honest con 1>", "<honest con 2>"],
  "difficulty_level": "beginner|intermediate|advanced",
  "use_cases": ["<who should read this 1>", "<who should read this 2>"],
  "summary": "<2 clear sentences about this book>"
}}"""


def research_single_product(product: dict) -> ResearchData:
    reviews_text = "\n".join([f"- {r}" for r in product["reviews"]])

    prompt = RESEARCH_PROMPT.format(
        title=product["title"],
        author=product["author"],
        price=product["price"],
        rating=product["rating"],
        description=product["description"],
        reviews=reviews_text,
        product_id=product["id"]
    )

    response = nvidia_fast.invoke(prompt)
    raw = response.content.strip()
    raw = re.sub(r"```(?:json)?", "", raw).strip()

    try:
        data = json.loads(raw)
        return ResearchData(
            product_id=product["id"],
            title=product["title"],
            pros=data.get("pros", []),
            cons=data.get("cons", []),
            difficulty_level=data.get("difficulty_level", "intermediate"),
            use_cases=data.get("use_cases", []),
            summary=data.get("summary", product["description"])
        )
    except json.JSONDecodeError:
        # Safe fallback if LLM returns bad JSON
        return ResearchData(
            product_id=product["id"],
            title=product["title"],
            pros=["Highly rated by readers"],
            cons=["Limited information available"],
            difficulty_level="intermediate",
            use_cases=["General learning"],
            summary=product["description"]
        )


def research_node(state: EcommerceState) -> dict:
    print(f"\n📖 [RESEARCH] Analyzing {len(state['product_list'])} products...")

    research_results = []

    for product in state["product_list"]:
        print(f"  🔎 Researching: {product['title'][:45]}...")
        result = research_single_product(product)
        research_results.append(result)
        print(f"     Difficulty: {result['difficulty_level']} | Pros: {len(result['pros'])} | Cons: {len(result['cons'])}")

    print(f"  ✅ Research complete for {len(research_results)} books")

    return {
        "research_data": research_results,
        "current_node": "research"
    }
