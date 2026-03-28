from fastapi import APIRouter, HTTPException
from api.models import (
    ChatRequest, ChatResponse, ProductResponse, RankedProduct,
    OrderRequest, OrderResponse,
    TrackRequest, TrackResponse,
    ReturnRequest, ReturnResponse,
    HistoryItem
)
from graph.workflow import app as langgraph_app
from state.schema   import EcommerceState
from memory.conversation_store import (
    save_turn, get_history, get_last_context, clear_session
)
from tools.db_tool import (
    place_order, get_order, get_product_by_id,
    initiate_return, search_products, get_all_categories, get_price_range
)
from typing import List

router = APIRouter()


# ── /chat ───────────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse, tags=["Core"])
async def chat(request: ChatRequest):
    """
    Main conversational endpoint.
    Runs the full LangGraph multi-agent pipeline.
    Maintains session memory across calls.
    """
    session_id   = request.session_id
    history      = get_history(session_id)
    last_context = get_last_context(session_id)

    initial_state: EcommerceState = {
        "session_id":             session_id,
        "user_query":             request.query,
        "conversation_history":   history,
        "intent":                 "",
        "plan":                   [],
        "budget":                 last_context.get("budget"),
        "category":               last_context.get("category"),
        "product_list":           [],
        "research_data":          [],
        "comparison_result":      None,
        "final_answer":           "",
        "recommended_product_id": last_context.get("product_id"),
        "validation_score":       0.0,
        "validation_feedback":    None,
        "retry_count":            0,
        "order_status":           None,
        "order_id":               last_context.get("order_id"),
        "error":                  None,
        "current_node":           "start"
    }

    try:
        final_state = langgraph_app.invoke(initial_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save turn to memory
    save_turn(
        session_id=session_id,
        user_query=request.query,
        assistant_response=final_state["final_answer"],
        intent=   final_state.get("intent"),
        category= final_state.get("category"),
        budget=   final_state.get("budget"),
        product_id=final_state.get("recommended_product_id"),
        order_id=  final_state.get("order_id"),
    )

    # Build recommended product response
    recommended_product = None
    if final_state.get("recommended_product_id"):
        p = get_product_by_id(final_state["recommended_product_id"])
        if p:
            recommended_product = ProductResponse(
                id=p["id"], title=p["title"], author=p["author"],
                price=p["price"], rating=p["rating"],
                category=p["category"], description=p["description"]
            )

    # Build ranked products response
    ranked_products = None
    comparison = final_state.get("comparison_result")
    if comparison and comparison.get("ranked_products"):
        ranked_products = [
            RankedProduct(
                rank=r.get("rank", i+1),
                product_id=r["product_id"],
                title=r["title"],
                total_score=float(r.get("total_score", 0)),
                price_value=r.get("price_value"),
                beginner_friendly=r.get("beginner_friendly"),
                content_depth=r.get("content_depth"),
                rating_score=r.get("rating_score"),
            )
            for i, r in enumerate(comparison["ranked_products"])
            if isinstance(r, dict) and "product_id" in r
        ]

    return ChatResponse(
        session_id=          session_id,
        intent=              final_state.get("intent", ""),
        answer=              final_state["final_answer"],
        recommended_product= recommended_product,
        ranked_products=     ranked_products,
        order_id=            final_state.get("order_id"),
        order_status=        final_state.get("order_status"),
        validation_score=    final_state.get("validation_score"),
    )


# ── /order ──────────────────────────────────────────────────────────────────

@router.post("/order", response_model=OrderResponse, tags=["Orders"])
async def place_order_endpoint(request: OrderRequest):
    """Place an order for a specific product by ID."""
    product = get_product_by_id(request.product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {request.product_id} not found")

    order_id = place_order(product_id=request.product_id, user_id=request.session_id)

    save_turn(
        session_id=request.session_id,
        user_query=f"Ordered product {request.product_id}",
        assistant_response=f"Order {order_id} placed",
        intent="order",
        product_id=request.product_id,
        order_id=order_id,
    )

    return OrderResponse(
        order_id=   order_id,
        product_id= request.product_id,
        status=     "confirmed",
        message=    f"Order placed for '{product['title']}'. Estimated delivery: 3-5 business days."
    )


# ── /track ──────────────────────────────────────────────────────────────────

@router.get("/track/{order_id}", response_model=TrackResponse, tags=["Orders"])
async def track_order(order_id: str):
    """Track a specific order by Order ID."""
    order = get_order(order_id.upper())
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

    return TrackResponse(
        order_id=        order["order_id"],
        status=          order["status"],
        delivery_status= order["delivery_status"],
        location=        order["location"],
        eta=             order["eta"],
        title=           order["title"],
        price=           order["price"],
    )


# ── /return ─────────────────────────────────────────────────────────────────

@router.post("/return", response_model=ReturnResponse, tags=["Orders"])
async def return_order(request: ReturnRequest):
    """Initiate a return for an order."""
    result = initiate_return(
        order_id=  request.order_id,
        reason=    request.reason,
        user_id=   request.session_id
    )

    if result is None:
        raise HTTPException(status_code=404,
                            detail=f"Order {request.order_id} not found")
    if result == "EXPIRED":
        raise HTTPException(status_code=400,
                            detail="Return window expired (7 days)")
    if result == "ALREADY_CANCELLED":
        raise HTTPException(status_code=400,
                            detail="Order already cancelled")

    return ReturnResponse(
        return_id= result,
        order_id=  request.order_id,
        status=    "initiated",
        message=   "Return initiated. Pickup scheduled within 2 business days. Refund in 3-5 days."
    )


# ── /history ────────────────────────────────────────────────────────────────

@router.get("/history/{session_id}", response_model=List[HistoryItem], tags=["Memory"])
async def get_session_history(session_id: str, limit: int = 10):
    """Get conversation history for a session."""
    history = get_history(session_id, limit=limit)
    return [
        HistoryItem(
            role=      h["role"],
            content=   h["content"],
            intent=    h.get("intent"),
            category=  h.get("category"),
            created_at=h.get("created_at"),
        )
        for h in history
    ]


@router.delete("/history/{session_id}", tags=["Memory"])
async def clear_session_history(session_id: str):
    """Clear all conversation history for a session."""
    clear_session(session_id)
    return {"message": f"Session {session_id} cleared successfully"}


# ── /products ───────────────────────────────────────────────────────────────

@router.get("/products", response_model=List[ProductResponse], tags=["Products"])
async def list_products(
    category:  str   = None,
    max_price: float = None,
    limit:     int   = 10
):
    """Browse products with optional filters."""
    products = search_products(
        category=  category,
        max_price= max_price,
        min_rating=4.0,
        limit=     limit
    )
    return [
        ProductResponse(
            id=p["id"], title=p["title"], author=p["author"],
            price=p["price"], rating=p["rating"],
            category=p["category"], description=p["description"]
        )
        for p in products
    ]


@router.get("/products/{product_id}", response_model=ProductResponse, tags=["Products"])
async def get_product(product_id: int):
    """Get a single product by ID."""
    product = get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return ProductResponse(
        id=product["id"], title=product["title"], author=product["author"],
        price=product["price"], rating=product["rating"],
        category=product["category"], description=product["description"]
    )


@router.get("/products/meta/categories", tags=["Products"])
async def list_categories():
    """List all available book categories."""
    return {"categories": get_all_categories()}


@router.get("/products/meta/price-range", tags=["Products"])
async def price_range():
    """Get min/max/avg price across all products."""
    return get_price_range()


# ── /health ─────────────────────────────────────────────────────────────────

@router.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status":  "healthy",
        "service": "multi-agent-ecommerce",
        "version": "1.0.0",
        "agents":  ["planner", "search", "research",
                    "comparison", "recommendation", "critic", "action"]
    }
