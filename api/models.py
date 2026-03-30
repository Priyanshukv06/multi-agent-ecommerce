from pydantic import BaseModel, Field
from typing import Optional, List


# ── Request Models ──────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query:      str = Field(..., min_length=1, max_length=500)
    session_id: str = Field(..., min_length=1, max_length=100)

    model_config = {"json_schema_extra": {"example": {
        "query":      "I want a ML book under ₹1000",
        "session_id": "user-123"
    }}}


class OrderRequest(BaseModel):
    product_id: int = Field(..., gt=0)
    session_id: str

    model_config = {"json_schema_extra": {"example": {
        "product_id": 1,
        "session_id": "user-123"
    }}}


class TrackRequest(BaseModel):
    order_id:   str
    session_id: str

    model_config = {"json_schema_extra": {"example": {
        "order_id":   "ORD-00001",
        "session_id": "user-123"
    }}}


class ReturnRequest(BaseModel):
    order_id:   str
    reason:     str = Field(default="Not specified")
    session_id: str

    model_config = {"json_schema_extra": {"example": {
        "order_id":   "ORD-00001",
        "reason":     "Wrong item received",
        "session_id": "user-123"
    }}}


# ── Response Models ─────────────────────────────────────────────────────────

class ProductResponse(BaseModel):
    id:          int
    title:       str
    author:      str
    price:       float
    rating:      float
    category:    str
    description: str
    cover_url:   str | None = None


class RankedProduct(BaseModel):
    rank:              int
    product_id:        int
    title:             str
    total_score:       float
    price_value:       Optional[float] = None
    beginner_friendly: Optional[float] = None
    content_depth:     Optional[float] = None
    rating_score:      Optional[float] = None


class ChatResponse(BaseModel):
    session_id:            str
    intent:                str
    answer:                str
    recommended_product:   Optional[ProductResponse] = None
    ranked_products:       Optional[List[RankedProduct]] = None
    order_id:              Optional[str] = None
    order_status:          Optional[str] = None
    validation_score:      Optional[float] = None


class OrderResponse(BaseModel):
    order_id:     str
    product_id:   int
    status:       str
    message:      str


class TrackResponse(BaseModel):
    order_id:        str
    status:          str
    delivery_status: str
    location:        str
    eta:             str
    title:           str
    price:           float


class ReturnResponse(BaseModel):
    return_id: str
    order_id:  str
    status:    str
    message:   str


class HistoryItem(BaseModel):
    role:       str
    content:    str
    intent:     Optional[str]  = None
    category:   Optional[str]  = None
    created_at: Optional[str]  = None


class ErrorResponse(BaseModel):
    error:   str
    detail:  Optional[str] = None
