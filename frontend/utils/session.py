import streamlit as st
import uuid
import json
import os
import time

SESSIONS_FILE = "data/sessions.json"


def init_session():
    """Initialize all session state variables."""
    defaults = {
        "session_id":    str(uuid.uuid4()),
        "messages":      [],
        "cart":          [],           # list of product dicts
        "last_order_id": None,
        "last_product":  None,
        "ranked":        [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def load_sessions() -> dict:
    if not os.path.exists(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_session(session_id: str, label: str):
    sessions = load_sessions()
    if session_id not in sessions:
        sessions[session_id] = {
            "label":      label[:40],
            "created_at": time.strftime("%d %b %Y %H:%M")
        }
        os.makedirs("data", exist_ok=True)
        with open(SESSIONS_FILE, "w") as f:
            json.dump(sessions, f, indent=2)


def delete_saved_session(session_id: str):
    sessions = load_sessions()
    sessions.pop(session_id, None)
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)


# ── Cart Helpers ─────────────────────────────────────────────────────────────
def add_to_cart(product: dict):
    cart = st.session_state.get("cart", [])
    if not any(p["id"] == product["id"] for p in cart):
        cart.append(product)
        st.session_state.cart = cart


def remove_from_cart(product_id: int):
    st.session_state.cart = [
        p for p in st.session_state.get("cart", [])
        if p["id"] != product_id
    ]


def clear_cart():
    st.session_state.cart = []


def cart_total() -> float:
    return sum(p["price"] for p in st.session_state.get("cart", []))


def in_cart(product_id: int) -> bool:
    return any(p["id"] == product_id
               for p in st.session_state.get("cart", []))