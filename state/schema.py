from typing import TypedDict, List, Optional, Literal

class ProductItem(TypedDict):
    id: int
    title: str
    author: str
    price: float
    rating: float
    category: str
    description: str
    reviews: List[str]

class ResearchData(TypedDict):
    product_id: int
    title: str
    pros: List[str]
    cons: List[str]
    difficulty_level: Literal["beginner", "intermediate", "advanced"]
    use_cases: List[str]
    summary: str

class ComparisonResult(TypedDict):
    ranked_products: List[dict]   # sorted best → worst
    best_choice_id: int
    scoring_table: List[dict]     # price_score, rating_score, difficulty_score
    reasoning: str

class EcommerceState(TypedDict):
    # Input
    user_query: str
    conversation_history: List[dict]      # for Phase 6 memory

    # Planner outputs
    intent: Literal["recommendation", "order", "return", "track", "compare", "faq"]
    plan: List[str]                        # ["search", "research", "compare", "recommend"]
    budget: Optional[float]               # extracted from query e.g. 1000.0
    category: Optional[str]              # e.g. "machine learning"

    # Search Agent outputs
    product_list: List[ProductItem]

    # Research Agent outputs
    research_data: List[ResearchData]

    # Comparison Agent outputs
    comparison_result: Optional[ComparisonResult]

    # Recommendation Agent outputs
    final_answer: str
    recommended_product_id: Optional[int]

    # Critic Agent outputs
    validation_score: float               # 0.0 to 1.0
    validation_feedback: Optional[str]   # critique if score < threshold
    retry_count: int                      # guard against infinite loops

    # Action Agent outputs
    order_status: Optional[str]          # "placed", "failed", "pending"
    order_id: Optional[str]

    # System
    error: Optional[str]
    current_node: str                    # tracks which agent is running (for UI)
