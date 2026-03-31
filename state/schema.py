from typing import TypedDict, List, Optional, Literal, Annotated
import operator


class ProductItem(TypedDict):
    id:          int
    title:       str
    author:      str
    price:       float
    rating:      float
    category:    str
    description: str
    reviews:     List[str]
    cover_url:   Optional[str]


class ResearchData(TypedDict):
    product_id:       int
    title:            str
    pros:             List[str]
    cons:             List[str]
    difficulty_level: Literal["beginner", "intermediate", "advanced"]
    use_cases:        List[str]
    summary:          str


class ComparisonResult(TypedDict):
    ranked_products: List[dict]
    best_choice_id:  int
    scoring_table:   List[dict]
    reasoning:       str


class EcommerceState(TypedDict):
    # ── Session ───────────────────────────────────────────────────────────────
    session_id:   str
    user_id:      Optional[str]          # ← ADD THIS

    # ── Input ─────────────────────────────────────────────────────────────────
    user_query:           str
    conversation_history: List[dict]

    # ── Planner ───────────────────────────────────────────────────────────────
    intent:   str
    plan:     List[str]
    budget:   Optional[float]
    category: Optional[str]

    # ── Search ────────────────────────────────────────────────────────────────
    product_list: List[ProductItem]

    # ── Research ──────────────────────────────────────────────────────────────
    research_data: Annotated[List[ResearchData], operator.add]

    # ── Comparison ────────────────────────────────────────────────────────────
    comparison_result: Optional[ComparisonResult]

    # ── Recommendation ────────────────────────────────────────────────────────
    final_answer:           str
    recommended_product_id: Optional[int]

    # ── Critic ────────────────────────────────────────────────────────────────
    validation_score:    float
    validation_feedback: Optional[str]
    retry_count:         int

    # ── Action ────────────────────────────────────────────────────────────────
    order_status: Optional[str]
    order_id:     Optional[str]

    # ── System ────────────────────────────────────────────────────────────────
    error:        Optional[str]
    current_node: str