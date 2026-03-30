import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)

import requests
from config.settings import API_BASE_URL


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get(endpoint: str, params: dict = None):
    try:
        resp = requests.get(
            f"{API_BASE_URL}{endpoint}",
            params=params,
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        return {"error": "API server is not running. Start it with: uvicorn api.main:app --reload"}
    except requests.Timeout:
        return {"error": "Request timed out. API is taking too long."}
    except Exception as e:
        return {"error": str(e)}


def _post(endpoint: str, data: dict, timeout: int = 30):
    try:
        resp = requests.post(
            f"{API_BASE_URL}{endpoint}",
            json=data,
            timeout=timeout
        )
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        return {"error": "API server is not running. Start it with: uvicorn api.main:app --reload"}
    except requests.Timeout:
        return {"error": "Request timed out. API is taking too long."}
    except Exception as e:
        return {"error": str(e)}


def _delete(endpoint: str):
    try:
        resp = requests.delete(f"{API_BASE_URL}{endpoint}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


# ── AI Chat ───────────────────────────────────────────────────────────────────

def call_chat(query: str, session_id: str) -> dict:
    return _post("/chat", {"query": query, "session_id": session_id}, timeout=120)


# ── Products ──────────────────────────────────────────────────────────────────

def get_products(
    category:  str   = None,
    max_price: float = None,
    limit:     int   = 50
) -> list:
    params = {"limit": limit}
    if category:
        params["category"]  = category
    if max_price:
        params["max_price"] = max_price
    result = _get("/products", params=params)
    if isinstance(result, list):
        return result
    return []


def get_product(product_id: int) -> dict:
    result = _get(f"/products/{product_id}")
    if isinstance(result, dict) and "error" not in result:
        return result
    return {}


def get_categories() -> list:
    result = _get("/products/meta/categories")
    if isinstance(result, dict):
        return result.get("categories", [])
    return []


def get_price_range() -> dict:
    result = _get("/products/meta/price-range")
    if isinstance(result, dict) and "error" not in result:
        return result
    return {"min": 300, "max": 1500, "avg": 800}


# ── Orders ────────────────────────────────────────────────────────────────────

def place_order(product_id: int, session_id: str) -> dict:
    return _post("/order", {"product_id": product_id, "session_id": session_id})


def place_bulk_orders(product_ids: list, session_id: str) -> list:
    """Place multiple orders one by one, return list of results."""
    return [place_order(pid, session_id) for pid in product_ids]


def track_order(order_id: str) -> dict:
    return _get(f"/track/{order_id}")


# ── Returns ───────────────────────────────────────────────────────────────────

def initiate_return(order_id: str, reason: str, session_id: str) -> dict:
    return _post("/return", {
        "order_id":   order_id,
        "reason":     reason,
        "session_id": session_id
    })


# ── Memory / History ──────────────────────────────────────────────────────────

def get_history(session_id: str, limit: int = 50) -> list:
    result = _get(f"/history/{session_id}", params={"limit": limit})
    if isinstance(result, list):
        return result
    return []


def clear_history(session_id: str):
    return _delete(f"/history/{session_id}")


# ── Health ────────────────────────────────────────────────────────────────────

def health_check() -> dict:
    return _get("/health")