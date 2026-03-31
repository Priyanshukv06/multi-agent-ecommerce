import streamlit as st
import sys
import os
import requests
sys.path.insert(0, os.path.dirname(__file__))

def _wake_up_api():
    """Ping Render to wake it from cold start — shows spinner while waiting."""
    try:
        import streamlit as st
        api_url = st.secrets.get("API_URL", os.getenv("API_URL", "http://localhost:8000"))
        
        with st.spinner("🔄 Connecting to server... (first load may take ~30 seconds)"):
            resp = requests.get(f"{api_url}/api/v1/health", timeout=60)
            if resp.status_code == 200:
                return True
    except Exception:
        pass
    return False

_wake_up_api()

# ── MUST be first Streamlit call ──────────────────────────────────────────────
st.set_page_config(
    page_title="AI Book Store",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.session import show_login_register, render_sidebar_user

# ── AUTH GATE ─────────────────────────────────────────────────────────────────
if "user" not in st.session_state or not st.session_state["user"]:
    show_login_register()
    st.stop()
# ─────────────────────────────────────────────────────────────────────────────

render_sidebar_user()

from utils.session import init_session
from utils.api     import get_products, get_categories


st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .hero-title {
        font-size: 48px; font-weight: 800;
        color: #e94560; text-align: center;
        margin-bottom: 8px;
    }
    .hero-sub {
        font-size: 16px; color: #606070;
        text-align: center; margin-bottom: 32px;
    }
    .feature-card {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 12px; padding: 20px;
        text-align: center; min-height: 160px;
    }
    .feature-icon { font-size: 36px; }
    .feature-title {
        font-size: 16px; font-weight: 700;
        color: #e0e0e0; margin: 8px 0 4px;
    }
    .feature-desc { font-size: 13px; color: #606070; }
    .stat-box {
        background: #16213e; border: 1px solid #0f3460;
        border-radius: 10px; padding: 16px;
        text-align: center;
    }
    .stat-num   { font-size: 32px; font-weight: 800; color: #e94560; }
    .stat-label { font-size: 13px; color: #808090; }
    .top-book-card {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 10px; padding: 14px;
        text-align: center; min-height: 130px;
    }
</style>
""", unsafe_allow_html=True)

init_session()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">📚 AI Book Store</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">'
    'Powered by LangGraph · 7 AI Agents · NVIDIA + Groq LLMs'
    '</div>',
    unsafe_allow_html=True
)

# ── Stats Row ─────────────────────────────────────────────────────────────────
products   = get_products(limit=100)
categories = get_categories()

c1, c2, c3, c4 = st.columns(4)
stats = [
    (str(len(products)),   "Books Available"),
    (str(len(categories)), "Categories"),
    ("7",                  "AI Agents"),
    ("< 30s",              "Avg Response"),
]
for col, (num, label) in zip([c1, c2, c3, c4], stats):
    with col:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-num">{num}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature Cards ─────────────────────────────────────────────────────────────
st.markdown("## What can you do here?")
f1, f2, f3 = st.columns(3)
features = [
    ("🛍️", "Browse & Buy",
     "Browse all books, filter by category and price, add to cart, buy instantly."),
    ("🤖", "AI Assistant",
     "Get personalized recommendations and comparisons from 7 LangGraph agents."),
    ("📦", "Order Management",
     "Track all your orders with a real-time timeline, manage returns easily."),
]
for col, (icon, title, desc) in zip([f1, f2, f3], features):
    with col:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-icon">{icon}</div>
            <div class="feature-title">{title}</div>
            <div class="feature-desc">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Navigation Buttons ────────────────────────────────────────────────────────
b1, b2, b3, b4 = st.columns(4)
with b1:
    if st.button("🛍️ Browse Books", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Browse.py")
with b2:
    if st.button("🤖 AI Assistant", use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")
with b3:
    if st.button("📦 My Orders",    use_container_width=True):
        st.switch_page("pages/3_Orders.py")
with b4:
    if st.button("🛒 My Cart",      use_container_width=True):
        st.switch_page("pages/5_Cart.py")

st.divider()

# ── Top Rated Books ───────────────────────────────────────────────────────────
st.markdown("## 🔥 Top Rated Books")
top_books = sorted(products, key=lambda x: x.get("rating", 0), reverse=True)[:4]

cols = st.columns(4)
for col, book in zip(cols, top_books):
    with col:
        st.markdown(f"""
        <div class="top-book-card">
            <div style='font-size:13px; font-weight:700;
                        color:#e94560; min-height:40px;'>
                {book["title"][:35]}...
            </div>
            <div style='font-size:12px; color:#808090; margin:4px 0;'>
                {book["author"][:22]}
            </div>
            <div style='color:#4caf50; font-size:13px;'>
                ⭐ {book["rating"]}/5
            </div>
            <div style='color:#e94560; font-weight:700; margin-top:4px;'>
                ₹{book["price"]}
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View", key=f"home_view_{book['id']}",
                     use_container_width=True):
            st.session_state.detail_product_id = book["id"]
            st.switch_page("pages/4_Book_Detail.py")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📚 AI Book Store")
    st.caption(f"Session: `{st.session_state.session_id[:16]}...`")
    st.divider()

    cart  = st.session_state.get("cart", [])
    total = sum(p["price"] for p in cart)

    if cart:
        st.markdown(f"### 🛒 Cart ({len(cart)} items)")
        for p in cart:
            st.caption(f"• {p['title'][:28]}... — ₹{p['price']}")
        st.markdown(f"**Total: ₹{total:.0f}**")
        if st.button("🛒 View Cart →", use_container_width=True, type="primary"):
            st.switch_page("pages/5_Cart.py")
    else:
        st.caption("🛒 Cart is empty")
        if st.button("🛍️ Start Shopping", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Browse.py")

    st.divider()

    st.markdown("**Navigation**")
    if st.button("🛍️ Browse Books", use_container_width=True):
        st.switch_page("pages/1_Browse.py")
    if st.button("🤖 AI Assistant", use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")
    if st.button("📦 My Orders",    use_container_width=True):
        st.switch_page("pages/3_Orders.py")

    st.divider()
    st.caption("Built with LangGraph + FastAPI + Streamlit")