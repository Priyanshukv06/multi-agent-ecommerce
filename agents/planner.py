import json
import re
from state.schema import EcommerceState
from tools.llm_config import groq_llm

PLANNER_PROMPT = """You are an intent classifier for an AI e-commerce book assistant.

Analyze the user query and extract:
1. intent: one of [recommendation, order, return, track, compare, faq]
2. category: book category (machine learning, deep learning, python, nlp, data science, mathematics, reinforcement learning, software engineering) or null
3. budget: numeric budget in INR or null
4. plan: list of steps needed

Rules:
- "buy", "purchase", "order" → intent: order
- "return", "refund", "cancel" → intent: return  
- "where is", "track", "status" → intent: track
- "compare", "difference between", "vs" → intent: compare
- "recommend", "suggest", "best", "good book", "learn" → intent: recommendation
- Extract budget from phrases like "under ₹1000", "below 500", "less than 800"

User query: "{query}"

Respond in strict JSON only — no explanation, no markdown:
{{"intent": "<intent>", "category": "<category or null>", "budget": <number or null>, "plan": ["<step1>", "<step2>"]}}"""


def planner_node(state: EcommerceState) -> dict:
    print(f"\n🧠 [PLANNER] Analyzing: '{state['user_query']}'")

    response = groq_llm.invoke(PLANNER_PROMPT.format(query=state["user_query"]))

    raw = response.content.strip()

    # Strip markdown code blocks if present
    raw = re.sub(r"```(?:json)?", "", raw).strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback safe defaults
        parsed = {
            "intent": "recommendation",
            "category": None,
            "budget": None,
            "plan": ["search", "research", "compare", "recommend"]
        }

    intent = parsed.get("intent", "recommendation")

    # Auto-define plan based on intent
    plan_map = {
        "recommendation": ["search", "research", "compare", "recommend"],
        "compare":        ["search", "research", "compare", "recommend"],
        "order":          ["action"],
        "return":         ["action"],
        "track":          ["action"],
        "faq":            ["recommend"],
    }

    print(f"  ✅ Intent: {intent} | Category: {parsed.get('category')} | Budget: ₹{parsed.get('budget')}")

    return {
        "intent":   intent,
        "category": parsed.get("category"),
        "budget":   parsed.get("budget"),
        "plan":     plan_map.get(intent, ["search", "research", "compare", "recommend"]),
        "retry_count": 0,
        "current_node": "planner"
    }
