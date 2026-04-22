import streamlit as st
import uuid
import json
import os
import time
import sys
import hashlib


# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from config.settings import SECRET_KEY     # ← Phase 11.3 addition

SESSIONS_FILE = os.path.join(ROOT, "data", "sessions.json")


# ════════════════════════════════════════════════════════════════════════════
# SESSION INIT
# ════════════════════════════════════════════════════════════════════════════
def init_session():
    """Initialize all session state variables with safe defaults."""
    defaults = {
        "session_id":        str(uuid.uuid4()),
        "messages":          [],
        "cart":              [],
        "cart_quantities":   {},
        "last_order_id":     None,
        "last_product":      None,
        "ranked":            [],
        "ai_prefill":        None,
        "buy_now_product":   None,
        "order_success":     None,
        "checkout_results":  None,
        "detail_product_id": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ════════════════════════════════════════════════════════════════════════════
# SECURE SESSION ID  ← Phase 11.3 addition
# ════════════════════════════════════════════════════════════════════════════
def generate_session_id(username: str) -> str:
    """Generate a consistent, secure session ID tied to username + SECRET_KEY."""
    raw = f"{username}:{SECRET_KEY}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# ════════════════════════════════════════════════════════════════════════════
# SAVED SESSIONS (with user isolation)
# ════════════════════════════════════════════════════════════════════════════
def load_sessions(user_id: int = None) -> dict:
    """Load sessions. If user_id provided, filter to that user only."""
    if not os.path.exists(SESSIONS_FILE):
        return {}
    try:
        with open(SESSIONS_FILE, "r") as f:
            all_sessions = json.load(f)
        
        # Filter by user_id if provided
        if user_id is not None:
            return {
                sid: meta for sid, meta in all_sessions.items()
                if meta.get("user_id") == user_id
            }
        return all_sessions
    except Exception:
        return {}


def save_session(session_id: str, label: str, user_id: int):
    """Save a session with user isolation."""
    sessions = load_sessions()  # Load all sessions
    if session_id not in sessions:
        os.makedirs(os.path.dirname(SESSIONS_FILE), exist_ok=True)
        sessions[session_id] = {
            "user_id":    user_id,  # ← ADD: user isolation
            "label":      label[:40],
            "created_at": time.strftime("%d %b %Y %H:%M")
        }
        with open(SESSIONS_FILE, "w") as f:
            json.dump(sessions, f, indent=2)


def delete_saved_session(session_id: str):
    sessions = load_sessions()  # Load all sessions
    sessions.pop(session_id, None)
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f, indent=2)


# ════════════════════════════════════════════════════════════════════════════
# CART HELPERS
# ════════════════════════════════════════════════════════════════════════════
def add_to_cart(product: dict):
    cart = st.session_state.get("cart", [])
    pid  = product.get("id")
    if not any(p.get("id") == pid for p in cart):
        cart.append(product)
        st.session_state["cart"] = cart
        qtys        = st.session_state.get("cart_quantities", {})
        qtys[pid]   = 1
        st.session_state["cart_quantities"] = qtys


def remove_from_cart(product_id: int):
    st.session_state["cart"] = [
        p for p in st.session_state.get("cart", [])
        if p.get("id") != product_id
    ]
    qtys = st.session_state.get("cart_quantities", {})
    qtys.pop(product_id, None)
    st.session_state["cart_quantities"] = qtys


def clear_cart():
    st.session_state["cart"]            = []
    st.session_state["cart_quantities"] = {}


def in_cart(product_id: int) -> bool:
    return any(
        p.get("id") == product_id
        for p in st.session_state.get("cart", [])
    )


def cart_total() -> float:
    cart = st.session_state.get("cart", [])
    qtys = st.session_state.get("cart_quantities", {})
    return sum(
        p.get("price", 0) * qtys.get(p.get("id"), 1)
        for p in cart
    )


def cart_count() -> int:                   # ← Phase 11.3 addition
    """Total number of items in cart (respects quantities)."""
    qtys = st.session_state.get("cart_quantities", {})
    return sum(qtys.values()) if qtys else len(st.session_state.get("cart", []))


# ════════════════════════════════════════════════════════════════════════════
# AUTH
# ════════════════════════════════════════════════════════════════════════════
def require_login():
    """
    Call at the top of every page.
    Stops rendering and shows login prompt if user is not in session.
    Returns the user dict if logged in.
    """
    if "user" not in st.session_state or not st.session_state.get("user"):
        st.warning("🔒 Please log in to continue.")
        st.page_link("app.py", label="← Go to Login", icon="🔑")
        st.stop()
    return st.session_state["user"]


def require_admin():
    """Restrict a page to admin role only."""
    user = require_login()
    if user.get("role") != "admin":
        st.error("⛔ Admin access only.")
        st.stop()
    return user


def logout():
    """Clear all session state and trigger rerun to show login."""
    st.session_state.clear()
    st.rerun()


def render_sidebar_user():
    """
    Renders the logged-in user badge + logout button at the
    bottom of the sidebar. Call after require_login() on each page.
    """
    user = st.session_state.get("user")
    if not user:
        return
    with st.sidebar:
        st.divider()
        role_badge = "👑 Admin" if user.get("role") == "admin" else "👤 User"
        st.markdown(f"**{role_badge}**")
        st.caption(f"Logged in as: `{user.get('username', '')}`")
        
        # Show Admin link only for admin users
        if user.get("role") == "admin":
            if st.button("👑 Admin Dashboard", use_container_width=True, type="primary"):
                st.switch_page("pages/6_Admin.py")
        
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout()


def show_login_register():
    """
    Full login + register UI rendered when user is not logged in.
    Call from app.py when 'user' is not in session_state.
    """
    from auth.auth import verify_password, get_user_by_username, create_user

    st.markdown("""
    <style>
    .auth-title {
        font-size: 2.2rem; font-weight: 800;
        color: #e94560; text-align: center; margin-bottom: 4px;
    }
    .auth-sub {
        font-size: 1rem; color: #a0a0b0;
        text-align: center; margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="auth-title">📚 AI Book Store</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="auth-sub">Multi-Agent AI powered recommendations</div>',
        unsafe_allow_html=True
    )

    tab_login, tab_register = st.tabs(["🔑 Sign In", "📝 Register"])

    # ── LOGIN ─────────────────────────────────────────────────────────────────
    with tab_login:
        with st.form("login_form", clear_on_submit=False):
            username  = st.text_input("Username", placeholder="Enter your username")
            password  = st.text_input("Password", type="password",
                                      placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True)

            if submitted:
                if not username.strip() or not password:
                    st.error("Please fill in all fields.")
                else:
                    db_user = get_user_by_username(username.strip())
                    if db_user and verify_password(password, db_user["password_hash"]):
                        st.session_state["user"] = {
                            "id":       db_user["id"],
                            "username": db_user["username"],
                            "role":     db_user["role"]
                        }
                        # ── Phase 11.3: use secure session ID per user ────────
                        st.session_state["session_id"] = generate_session_id(
                            db_user["username"]
                        )
                        st.success(f"Welcome back, {db_user['username']}! 🎉")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

        st.caption(
            "**Demo accounts:** `admin / admin123` · "
            "`user1 / user123` · `user2 / user123`"
        )

    # ── REGISTER ──────────────────────────────────────────────────────────────
    with tab_register:
        with st.form("register_form", clear_on_submit=True):
            new_username = st.text_input("Choose a Username",
                                         placeholder="Minimum 3 characters")
            new_password = st.text_input("Password", type="password",
                                          placeholder="Minimum 6 characters")
            confirm_pw   = st.text_input("Confirm Password", type="password",
                                          placeholder="Repeat your password")
            reg_submit   = st.form_submit_button("Create Account",
                                                  use_container_width=True)

            if reg_submit:
                if not new_username.strip() or not new_password or not confirm_pw:
                    st.error("Please fill in all fields.")
                elif len(new_username.strip()) < 3:
                    st.error("Username must be at least 3 characters.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif new_password != confirm_pw:
                    st.error("Passwords do not match.")
                else:
                    new_user = create_user(new_username.strip(), new_password,
                                           role="user")
                    if new_user:
                        st.session_state["user"] = new_user
                        # ── Phase 11.3: secure session ID on register ─────────
                        st.session_state["session_id"] = generate_session_id(
                            new_user["username"]
                        )
                        st.success(
                            f"Account created! Welcome, {new_user['username']}! 🎉"
                        )
                        st.rerun()
                    else:
                        st.error("❌ Username already taken. Try another.")