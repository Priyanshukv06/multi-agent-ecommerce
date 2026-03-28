import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from tools.llm_config import nvidia_llm, nvidia_fast, groq_llm
from tools.db_tool import search_products

def run_test(name, func):
    print(f"\n{'='*50}")
    try:
        func()
    except Exception as e:
        print(f"  ❌ FAILED: {name}")
        print(f"  Error: {str(e)[:200]}")

# ─── Test 1: Intent Classification (Groq) ──────────────────────────────────
def test_intent_classification():
    print("\n🧠 TEST 1: Intent Classification")
    queries = [
        "I want a good book to learn machine learning under ₹1000",
        "Buy me the top rated python book",
        "Where is my order ORD-00001",
        "Compare deep learning books",
        "Return my last order"
    ]
    prompt_template = """You are an intent classifier for an e-commerce assistant.
Classify the user query into exactly one of: recommendation, order, track, compare, return

User query: "{query}"

Respond in JSON only:
{{"intent": "<intent>", "category": "<product category or null>", "budget": <number or null>}}"""

    for q in queries:
        response = groq_llm.invoke(prompt_template.format(query=q))
        print(f"  Query: {q[:50]}...")
        print(f"  Result: {response.content}\n")


# ─── Test 2: Review Summarization (NVIDIA) ─────────────────────────────────
def test_review_summarization():
    print("\n🔍 TEST 2: Review Summarization (Research Agent)")
    products = search_products(category="machine learning", max_price=1000.0, limit=1)
    if not products:
        print("  No products found")
        return

    book = products[0]
    reviews_text = "\n".join([f"- {r}" for r in book["reviews"]])

    prompt = f"""Analyze these reviews for the book "{book['title']}" and extract structured insights.

Reviews:
{reviews_text}

Respond in JSON only:
{{
  "pros": ["<pro1>", "<pro2>", "<pro3>"],
  "cons": ["<con1>", "<con2>"],
  "difficulty_level": "beginner|intermediate|advanced",
  "use_cases": ["<use_case1>", "<use_case2>"],
  "summary": "<2 sentence summary>"
}}"""

    response = nvidia_fast.invoke(prompt)
    print(f"  Book: {book['title']}")
    print(f"  Research Output:\n{response.content}\n")


# ─── Test 3: Comparison (NVIDIA) ────────────────────────────────────────────
def test_comparison():
    print("\n⚖️  TEST 3: Comparison Agent")
    products = search_products(category="machine learning", max_price=1000.0, limit=3)
    if len(products) < 2:
        print("  Not enough products")
        return

    books_text = "\n".join([
        f"Book {i+1}: {b['title']} by {b['author']} | ₹{b['price']} | ⭐{b['rating']}"
        for i, b in enumerate(products)
    ])

    prompt = f"""Compare these books and rank them. User wants a machine learning book under ₹1000.

Books:
{books_text}

Score each book (0-10) on: price_value, beginner_friendly, content_depth, rating
Respond in JSON only:
{{
  "ranked": [
    {{"rank": 1, "title": "<title>", "price_value": 8, "beginner_friendly": 9, "content_depth": 8, "rating_score": 10, "total_score": 35}},
    ...
  ],
  "best_choice": "<title>",
  "reasoning": "<2 sentence reasoning>"
}}"""

    response = nvidia_fast.invoke(prompt)
    print(f"  Comparison Result:\n{response.content}\n")


# ─── Test 4: Recommendation Generation (NVIDIA Nemotron) ────────────────────
def test_recommendation():
    print("\n✍️  TEST 4: Recommendation Agent")
    prompt = """A user asked: "I want a good book to learn machine learning under ₹1000"

Based on analysis, the best recommendation is:
- Book: Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow
- Author: Aurélien Géron
- Price: ₹899
- Rating: 4.9/5
- Why best: Highest rating, practical approach, covers full ML pipeline

Generate a friendly, helpful recommendation response. Include:
1. Your recommendation with clear reasoning
2. 3 key reasons why this book fits their needs
3. One honest limitation
4. A closing encouragement

Keep it under 150 words. Sound like a knowledgeable friend, not a robot."""

    response = nvidia_llm.invoke(prompt)
    print(f"  Recommendation:\n{response.content}\n")


# ─── Test 5: Critic Validation (Groq) ───────────────────────────────────────
def test_critic():
    print("\n🧐 TEST 5: Critic/Validator Agent")
    recommendation = """I recommend 'Hands-On Machine Learning' by Aurélien Géron at ₹899.
It has a 4.9 rating and covers the full ML pipeline practically.
Perfect for beginners who know basic Python."""

    prompt = f"""You are a quality checker for an AI recommendation system.

User asked for: "ML book under ₹1000"
Recommendation given: "{recommendation}"

Check for:
1. Does it satisfy the budget constraint? (under ₹1000)
2. Is the reasoning clear and specific?
3. Any hallucinated facts or missing information?
4. Is it helpful for the user?

Respond in JSON only:
{{
  "score": <0.0 to 1.0>,
  "budget_satisfied": true/false,
  "reasoning_clear": true/false,
  "issues": ["<issue1 or empty list>"],
  "feedback": "<one sentence feedback or 'looks good'>",
  "verdict": "pass|retry"
}}"""

    response = groq_llm.invoke(prompt)
    print(f"  Critic Output:\n{response.content}\n")


# ─── Run all tests ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("🧪 PHASE 2: PROMPT TESTING — All Agent Capabilities")
    print("=" * 60)

    run_test("Intent Classification",   test_intent_classification)
    run_test("Review Summarization",    test_review_summarization)
    run_test("Comparison",              test_comparison)
    run_test("Recommendation",          test_recommendation)
    run_test("Critic Validation",       test_critic)

    print("\n" + "=" * 60)
    print("✅ All prompt tests complete!")
    print("=" * 60)