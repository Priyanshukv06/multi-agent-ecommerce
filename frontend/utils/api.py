import requests
import streamlit as st

API_BASE = "http://localhost:8000/api/v1"


def call_chat(query: str, session_id: str) -> dict:
    try:
        response = requests.post(f"{API_BASE}/chat", json={
            "query":      query,
            "session_id": session_id
        }, timeout=120)
        return response.json()
    except Exception as e:
        return {"answer": f"❌ API error: {str(e)}", "intent": "error"}


def get_products(category=None, max_price=None, limit=20) -> list:
    try:
        params = {"limit": limit}
        if category:  params["category"]  = category
        if max_price: params["max_price"] = max_price
        return requests.get(f"{API_BASE}/products", params=params, timeout=10).json()
    except Exception:
        return []


def get_product(product_id: int) -> dict:
    try:
        return requests.get(f"{API_BASE}/products/{product_id}", timeout=10).json()
    except Exception:
        return {}


def get_categories() -> list:
    try:
        return requests.get(f"{API_BASE}/products/meta/categories", timeout=10).json().get("categories", [])
    except Exception:
        return []


def get_price_range() -> dict:
    try:
        return requests.get(f"{API_BASE}/products/meta/price-range", timeout=10).json()
    except Exception:
        return {"min": 300, "max": 1500, "avg": 800}


def place_order(product_id: int, session_id: str) -> dict:
    try:
        return requests.post(f"{API_BASE}/order", json={
            "product_id": product_id,
            "session_id": session_id
        }, timeout=10).json()
    except Exception as e:
        return {"error": str(e)}


def place_bulk_orders(product_ids: list, session_id: str) -> list:
    results = []
    for pid in product_ids:
        results.append(place_order(pid, session_id))
    return results


def track_order(order_id: str) -> dict:
    try:
        return requests.get(f"{API_BASE}/track/{order_id}", timeout=10).json()
    except Exception as e:
        return {"error": str(e)}


def get_user_orders(session_id: str) -> list:
    try:
        # Reuse history endpoint to get orders from memory
        response = requests.get(
            f"{API_BASE}/history/{session_id}?limit=50", timeout=10
        )
        history = response.json()
        # Extract unique order IDs from memory
        order_ids = list({
            h["content"].split("`")[1]
            for h in history
            if h.get("role") == "assistant"
            and "ORD-" in h.get("content", "")
        })
        return order_ids
    except Exception:
        return []


def initiate_return(order_id: str, reason: str, session_id: str) -> dict:
    try:
        return requests.post(f"{API_BASE}/return", json={
            "order_id":   order_id,
            "reason":     reason,
            "session_id": session_id
        }, timeout=10).json()
    except Exception as e:
        return {"error": str(e)}


def get_history(session_id: str, limit: int = 20) -> list:
    try:
        return requests.get(
            f"{API_BASE}/history/{session_id}?limit={limit}", timeout=10
        ).json()
    except Exception:
        return []


def clear_history(session_id: str):
    try:
        requests.delete(f"{API_BASE}/history/{session_id}", timeout=10)
    except Exception:
        pass