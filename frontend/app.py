import streamlit as st
import requests
import uuid
import time

API_BASE = "http://localhost:8000/api/v1"

# ── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Book Store",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #0f1117; }

    /* Chat bubbles */
    .user-bubble {
        background: #1e3a5f;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #e8f4fd;
        font-size: 15px;
        max-width: 80%;
        float: right;
        clear: both;
    }
    .bot-bubble {
        background: #1a1a2e;
        border: 1px solid #2d2d4e;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        margin: 8px 0;
        color: #e0e0e0;
        font-size: 15px;
        max-width: 85%;
        float: left;
        clear: both;
    }

    /* Product card */
    .product-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid #0f3460;
        border-radius: 12px;
        padding: 16px;
        margin: 8px 0;
    }
    .product-title {
        font-size: 16px;
        font-weight: 700;
        color: #e94560;
        margin-bottom: 4px;
    }
    .product-meta {
        font-size: 13px;
        color: #a0a0b0;
    }
    .price-badge {
        background: #0f3460;
        color: #e94560;
        padding: 3px 10px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 14px;
    }
    .rating-badge {
        background: #1a3a1a;
        color: #4caf50;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 13px;
    }

    /* Score bar */
    .score-bar {
        background: #16213e;
        border-radius: 6px;
        padding: 10px 14px;
        margin: 4px 0;
        border-left: 3px solid #e94560;
        font-size: 13px;
        color: #c0c0d0;
    }

    /* Sidebar */
    .sidebar-header {
        font-size: 18px;
        font-weight: 700;
        color: #e94560;
        margin-bottom: 12px;
    }

    /* Input area */
    .stTextInput input {
        background: #1a1a2e !important;
        border: 1px solid #0f3460 !important;
        color: #e0e0e0 !important;
        border-radius: 12px !important;
    }

    /* Suggestion chips */
    .chip-container { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0; }
    .chip {
        background: #16213e;
        border: 1px solid #0f3460;
        border-radius: 20px;
        padding: 6px 14px;
        font-size: 13px;
        color: #a0c4ff;
        cursor: pointer;
    }

    /* Clear floats */
    .clearfix::after { content: ""; display: table; clear: both; }
</style>
""", unsafe_allow_html=True)


# ── Session State Init ───────────────────────────────────────────────────────
if "session_id"   not in st.session_state:
    st.session_state.session_id   = str(uuid.uuid4())
if "messages"     not in st.session_state:
    st.session_state.messages     = []
if "last_product" not in st.session_state:
    st.session_state.last_product = None
if "last_order"   not in st.session_state:
    st.session_state.last_order   = None
if "ranked"       not in st.session_state:
    st.session_state.ranked       = []


# ── API Helpers ──────────────────────────────────────────────────────────────
def call_chat(query: str) -> dict:
    try:
        response = requests.post(f"{API_BASE}/chat", json={
            "query":      query,
            "session_id": st.session_state.session_id
        }, timeout=120)
        return response.json()
    except Exception as e:
        return {"answer": f"❌ API error: {str(e)}", "intent": "error"}


def call_track(order_id: str) -> dict:
    try:
        response = requests.get(f"{API_BASE}/track/{order_id}", timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def get_history() -> list:
    try:
        response = requests.get(
            f"{API_BASE}/history/{st.session_state.session_id}",
            timeout=10
        )
        return response.json()
    except Exception:
        return []


def get_products(category=None, max_price=None) -> list:
    try:
        params   = {}
        if category:  params["category"]  = category
        if max_price: params["max_price"] = max_price
        response = requests.get(f"{API_BASE}/products", params=params, timeout=10)
        return response.json()
    except Exception:
        return []


def clear_session():
    try:
        requests.delete(
            f"{API_BASE}/history/{st.session_state.session_id}",
            timeout=10
        )
    except Exception:
        pass
    st.session_state.messages     = []
    st.session_state.session_id   = str(uuid.uuid4())
    st.session_state.last_product = None
    st.session_state.last_order   = None
    st.session_state.ranked       = []


# ── Render Helpers ───────────────────────────────────────────────────────────
def render_product_card(product: dict, show_scores: bool = False, rank: int = None):
    rank_label = f"#{rank} " if rank else ""
    st.markdown(f"""
    <div class="product-card">
        <div class="product-title">{rank_label}{product.get('title', '')}</div>
        <div class="product-meta">✍️ {product.get('author', '')}</div>
        <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;">
            <span class="price-badge">₹{product.get('price', '')}</span>
            <span class="rating-badge">⭐ {product.get('rating', '')}/5</span>
            <span style="background:#2d1a3e; color:#c084fc; padding:3px 10px;
                         border-radius:20px; font-size:13px;">
                📂 {product.get('category', '')}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if show_scores and product.get("total_score"):
        cols = st.columns(4)
        score_labels = [
            ("💰 Price",    "price_value"),
            ("🎓 Beginner", "beginner_friendly"),
            ("📖 Depth",    "content_depth"),
            ("⭐ Rating",   "rating_score"),
        ]
        for col, (label, key) in zip(cols, score_labels):
            with col:
                val = product.get(key, 0) or 0
                st.metric(label, f"{val}/10")


def render_chat_message(role: str, content: str):
    if role == "user":
        st.markdown(
            f'<div class="clearfix"><div class="user-bubble">👤 {content}</div></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="clearfix"><div class="bot-bubble">🤖 {content}</div></div>',
            unsafe_allow_html=True
        )


def handle_query(query: str):
    if not query.strip():
        return

    # Add user message
    st.session_state.messages.append({"role": "user", "content": query})

    # Call API with spinner
    with st.spinner("🤖 Thinking..."):
        start = time.time()
        result = call_chat(query)
        elapsed = round(time.time() - start, 1)

    answer = result.get("answer", "Sorry, something went wrong.")
    intent = result.get("intent", "")

    # Store context
    if result.get("recommended_product"):
        st.session_state.last_product = result["recommended_product"]
    if result.get("order_id"):
        st.session_state.last_order = result["order_id"]
    if result.get("ranked_products"):
        st.session_state.ranked = result["ranked_products"]

    # Add bot message with metadata
    st.session_state.messages.append({
        "role":    "assistant",
        "content": answer,
        "intent":  intent,
        "elapsed": elapsed,
        "data":    result
    })


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sidebar-header">📚 AI Book Store</div>',
                unsafe_allow_html=True)
    st.caption(f"Session: `{st.session_state.session_id[:16]}...`")

    st.divider()

    # ── Quick Actions ────────────────────────────────────────────────────────
    st.markdown("**⚡ Quick Actions**")

    quick_queries = [
        "📘 Best ML book under ₹1000",
        "🧠 Compare deep learning books",
        "🐍 Recommend a Python book",
        "📊 Data science books under ₹800",
        "📦 Show my orders",
    ]

    for q in quick_queries:
        if st.button(q, key=f"quick_{q}", use_container_width=True):
            handle_query(q.split(" ", 1)[1])   # strip emoji prefix
            st.rerun()

    st.divider()

    # ── Order Tracker ─────────────────────────────────────────────────────────
    st.markdown("**📦 Order Tracker**")
    track_input = st.text_input("Enter Order ID", placeholder="ORD-00001",
                                label_visibility="collapsed")
    if st.button("🔍 Track", use_container_width=True) and track_input:
        with st.spinner("Fetching order..."):
            order = call_track(track_input.upper())
        if "error" in order or "detail" in order:
            st.error("Order not found")
        else:
            st.success(f"**{order.get('delivery_status')}**")
            st.caption(f"📍 {order.get('location')}")
            st.caption(f"🏁 ETA: {order.get('eta')}")
            st.caption(f"📚 {order.get('title', '')[:40]}")

    # Show last order if exists
    if st.session_state.last_order:
        st.info(f"Last order: `{st.session_state.last_order}`")

    st.divider()

    # ── Browse Products ───────────────────────────────────────────────────────
    st.markdown("**🔎 Browse by Category**")
    categories = ["All", "machine learning", "deep learning", "python",
                  "data science", "mathematics", "nlp"]
    selected_cat = st.selectbox("Category", categories, label_visibility="collapsed")
    max_price    = st.slider("Max Price (₹)", 300, 1500, 1500, step=50)

    if st.button("🛍️ Browse", use_container_width=True):
        cat      = None if selected_cat == "All" else selected_cat
        products = get_products(category=cat, max_price=max_price)
        if products:
            st.markdown(f"**Found {len(products)} books:**")
            for p in products[:3]:
                st.markdown(f"• **{p['title'][:30]}...** ₹{p['price']}")
        else:
            st.warning("No products found")

    st.divider()

    # ── Session Controls ──────────────────────────────────────────────────────
    st.markdown("**⚙️ Session**")
    history_count = len(get_history())
    st.caption(f"💬 {history_count} messages in memory")

    if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
        clear_session()
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# MAIN CHAT AREA
# ════════════════════════════════════════════════════════════════════════════

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<h1 style='text-align:center; color:#e94560; margin-bottom:4px;'>
    📚 AI Book Store
</h1>
<p style='text-align:center; color:#606070; font-size:14px; margin-bottom:20px;'>
    Powered by LangGraph · 7 AI Agents · NVIDIA + Groq LLMs
</p>
""", unsafe_allow_html=True)


# ── Welcome message ───────────────────────────────────────────────────────────
if not st.session_state.messages:
    st.markdown("""
    <div style='background:#1a1a2e; border:1px solid #2d2d4e; border-radius:12px;
                padding:20px; text-align:center; margin-bottom:20px;'>
        <div style='font-size:40px; margin-bottom:8px;'>👋</div>
        <div style='color:#e0e0e0; font-size:16px; font-weight:600;'>
            Welcome to AI Book Store!
        </div>
        <div style='color:#808090; font-size:14px; margin-top:8px;'>
            Ask me to recommend, compare, or buy any tech book.
            I'll research and rank options just for you.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Suggestion chips
    st.markdown("**Try asking:**")
    col1, col2, col3 = st.columns(3)
    suggestions = [
        ("📘 ML under ₹1000",        "recommend a machine learning book under ₹1000"),
        ("🧠 Compare deep learning",  "compare deep learning books"),
        ("🐍 Best Python book",       "what is the best python programming book"),
        ("📊 Data science books",     "suggest data science books"),
        ("📦 Track my order",         "show my orders"),
        ("🔁 Return an order",        "I want to return my last order"),
    ]
    for i, (label, query) in enumerate(suggestions):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(label, key=f"sug_{i}", use_container_width=True):
                handle_query(query)
                st.rerun()


# ── Chat History ──────────────────────────────────────────────────────────────
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        render_chat_message(msg["role"], msg["content"])

        # Show product card after recommendation
        if msg["role"] == "assistant":
            data   = msg.get("data", {})
            intent = msg.get("intent", "")

            # Recommended product card
            if data.get("recommended_product") and intent in ("recommendation", "compare", "order"):
                with st.expander("📗 Recommended Book", expanded=True):
                    render_product_card(data["recommended_product"])

            # Ranked products comparison table
            if data.get("ranked_products") and len(data["ranked_products"]) > 1:
                with st.expander(f"📊 Comparison — {len(data['ranked_products'])} books scored"):
                    for p in data["ranked_products"]:
                        render_product_card(p, show_scores=True, rank=p.get("rank"))

            # Order confirmation
            if data.get("order_id") and intent == "order":
                st.success(f"✅ Order placed: `{data['order_id']}`")
                st.session_state.last_order = data["order_id"]

            # Response time
            if msg.get("elapsed"):
                st.caption(f"⏱️ {msg['elapsed']}s · Intent: `{intent}`")


# ── Chat Input ────────────────────────────────────────────────────────────────
st.divider()
col_input, col_send = st.columns([5, 1])

with col_input:
    user_input = st.chat_input("Ask me about books, orders, or anything...")

if user_input:
    handle_query(user_input)
    st.rerun()
