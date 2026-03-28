import json
import re
from state.schema import EcommerceState
from tools.llm_config import groq_llm
from memory.conversation_store import get_last_context, format_history_for_prompt

PLANNER_PROMPT = """You are an intent classifier for an AI e-commerce book assistant.

Recent Conversation:
{history}

Analyze the user query and extract:
1. intent: one of [recommendation, order, return, track, compare, faq]
2. category: book category or null
3. budget: numeric budget in INR or null
4. plan: list of steps needed

Rules:
- "buy", "purchase", "order", "buy it" → intent: order
- "return", "refund", "cancel" → intent: return
- "where is", "track", "status", "where" → intent: track
- "compare", "difference", "vs" → intent: compare
- "recommend", "suggest", "best", "learn" → intent: recommendation
- If user says "buy it" or "order it" with no product — check conversation history for last recommended product
- If category is not mentioned but history shows a category — reuse it
- Extract budget from "under ₹1000", "below 500", "less than 800"

User query: "{query}"

Respond in strict JSON only:
{{"intent": "<intent>", "category": "<category or null>", "budget": <number or null>, "plan": ["<step1>", "<step2>"]}}"""


def planner_node(state: EcommerceState) -> dict:
    print(f"\n🧠 [PLANNER] Analyzing: '{state['user_query']}'")

    # ── Load memory context ─────────────────────────────────────────────────
    session_id   = state.get("session_id", "default")
    last_context = get_last_context(session_id)
    history      = state.get("conversation_history", [])
    history_text = format_history_for_prompt(history) if history else "No previous conversation."

    response = groq_llm.invoke(
        PLANNER_PROMPT.format(
            query=state["user_query"],
            history=history_text
        )
    )

    raw = re.sub(r"```(?:json)?", "", response.content.strip()).strip()

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {
            "intent":   "recommendation",
            "category": None,
            "budget":   None,
            "plan":     ["search", "research", "compare", "recommend"]
        }

    intent = parsed.get("intent", "recommendation")

    plan_map = {
        "recommendation": ["search", "research", "compare", "recommend"],
        "compare":        ["search", "research", "compare", "recommend"],
        "order":          ["action"],
        "return":         ["action"],
        "track":          ["action"],
        "faq":            ["recommend"],
    }

    # ── Memory fallback: inherit context from last turn ─────────────────────
    category = parsed.get("category") or last_context.get("category")
    budget   = parsed.get("budget")   or last_context.get("budget")

    # For order intent — carry forward last recommended product
    recommended_product_id = state.get("recommended_product_id")
    if intent == "order" and not recommended_product_id:
        recommended_product_id = last_context.get("product_id")
        if recommended_product_id:
            print(f"  🧠 Memory: reusing last recommended product_id={recommended_product_id}")

    print(f"  ✅ Intent: {intent} | Category: {category} | Budget: ₹{budget}")

    return {
        "intent":                  intent,
        "category":                category,
        "budget":                  budget,
        "plan":                    plan_map.get(intent, ["search", "research", "compare", "recommend"]),
        "retry_count":             0,
        "current_node":            "planner",
        "recommended_product_id":  recommended_product_id,
    }
