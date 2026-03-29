import requests

API_BASE = "http://localhost:8000/api/v1"


def call_chat(query: str, session_id: str, user_id: int = None) -> dict:
    try:
        payload = {"query": query, "session_id": session_id}
        if user_id:
            payload["user_id"] = user_id
        response = requests.post(f"{API_BASE}/chat", json=payload, timeout=120)
        return response.json()
    except Exception as e:
        return {"answer": f"API error: {str(e)}", "intent": "error"}


def get_products(category=None, max_price=None, limit=20) -> list:
    try:
        params = {"limit": limit}
        if category:
            params["category"] = category
        if max_price:
            params["max_price"] = max_price
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
        return requests.get(
            f"{API_BASE}/products/meta/categories", timeout=10
        ).json().get("categories", [])
    except Exception:
        return []


def get_price_range() -> dict:
    try:
        return requests.get(
            f"{API_BASE}/products/meta/price-range", timeout=10
        ).json()
    except Exception:
        return {"min": 300, "max": 1500, "avg": 800}


def place_order(product_id: int, session_id: str,
                user_id: int = None, quantity: int = 1) -> dict:
    try:
        payload = {
            "product_id": product_id,
            "session_id": session_id,
            "quantity":   quantity,
        }
        if user_id:
            payload["user_id"] = user_id
        return requests.post(f"{API_BASE}/order", json=payload, timeout=10).json()
    except Exception as e:
        return {"error": str(e)}


def place_bulk_orders(items: list, session_id: str, user_id: int = None) -> list:
    """items: list of dicts with keys 'id' and 'quantity'"""
    results = []
    for item in items:
        pid = item.get("id") if isinstance(item, dict) else item
        qty = item.get("quantity", 1) if isinstance(item, dict) else 1
        results.append(place_order(pid, session_id, user_id=user_id, quantity=qty))
    return results


def track_order(order_id: str) -> dict:
    try:
        return requests.get(f"{API_BASE}/track/{order_id}", timeout=10).json()
    except Exception as e:
        return {"error": str(e)}


def initiate_return(order_id: str, reason: str,
                    session_id: str, user_id: int = None) -> dict:
    try:
        payload = {"order_id": order_id, "reason": reason, "session_id": session_id}
        if user_id:
            payload["user_id"] = user_id
        return requests.post(f"{API_BASE}/return", json=payload, timeout=10).json()
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