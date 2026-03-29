import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.session import init_session
from utils.api     import get_products, get_categories

st.set_page_config(
    page_title="AI Book Store",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        text-align: center; height: 160px;
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
    .stat-num { font-size: 32px; font-weight: 800; color: #e94560; }
    .stat-label { font-size: 13px; color: #808090; }
</style>
""", unsafe_allow_html=True)

init_session()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">📚 AI Book Store</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-sub">Powered by LangGraph · 7 AI Agents · NVIDIA + Groq LLMs</div>',
    unsafe_allow_html=True
)

# ── Stats Row ─────────────────────────────────────────────────────────────────
products   = get_products(limit=100)
categories = get_categories()

col1, col2, col3, col4 = st.columns(4)
stats = [
    (str(len(products)),      "Books Available"),
    (str(len(categories)),    "Categories"),
    ("7",                     "AI Agents"),
    ("< 30s",                 "Avg Response"),
]
for col, (num, label) in zip([col1, col2, col3, col4], stats):
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
c1, c2, c3 = st.columns(3)

features = [
    ("🛍️", "Browse & Buy",
     "Browse all books, filter by category and price, add to cart, buy instantly — no AI needed."),
    ("🤖", "AI Assistant",
     "Get personalized recommendations, comparisons, and analysis powered by 7 LangGraph agents."),
    ("📦", "Order Management",
     "Track all your orders in real-time, manage returns, view full order history."),
]
for col, (icon, title, desc) in zip([c1, c2, c3], features):
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
b1, b2, b3 = st.columns(3)
with b1:
    if st.button("🛍️ Browse Books", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Browse.py")
with b2:
    if st.button("🤖 AI Assistant", use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")
with b3:
    if st.button("📦 My Orders", use_container_width=True):
        st.switch_page("pages/3_Orders.py")

st.divider()

# ── Featured Books Preview ────────────────────────────────────────────────────
st.markdown("## 🔥 Top Rated Books")
top_books = sorted(products, key=lambda x: x.get("rating", 0), reverse=True)[:4]

cols = st.columns(4)
for col, book in zip(cols, top_books):
    with col:
        st.markdown(f"""
        <div style='background:#1a1a2e; border:1px solid #0f3460;
                    border-radius:10px; padding:12px; text-align:center;'>
            <div style='font-size:13px; font-weight:700; color:#e94560;
                        min-height:40px;'>{book["title"][:35]}...</div>
            <div style='font-size:12px; color:#808090; margin:4px 0;'>
                {book["author"][:20]}
            </div>
            <div style='color:#4caf50; font-size:13px;'>
                ⭐ {book["rating"]}/5
            </div>
            <div style='color:#e94560; font-weight:700; margin-top:4px;'>
                ₹{book["price"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Cart indicator in sidebar ─────────────────────────────────────────────────
with st.sidebar:
    cart = st.session_state.get("cart", [])
    if cart:
        st.markdown(f"### 🛒 Cart ({len(cart)} items)")
        total = sum(p["price"] for p in cart)
        for p in cart:
            st.caption(f"• {p['title'][:30]} — ₹{p['price']}")
        st.markdown(f"**Total: ₹{total}**")
        if st.button("Checkout →", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Browse.py")
    else:
        st.caption("🛒 Cart is empty")

    st.divider()
    st.caption(f"Session: `{st.session_state.session_id[:16]}...`")