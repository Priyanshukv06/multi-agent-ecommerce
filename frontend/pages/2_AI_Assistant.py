import streamlit as st
import sys
import os

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'frontend'))

st.set_page_config(
    page_title="AI Assistant — AI Book Store",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.api     import call_chat, get_history, clear_history, place_order
from utils.session import (init_session, save_session, load_sessions,
                           delete_saved_session, cart_total,
                           require_login, render_sidebar_user)
from utils.error   import show_api_error, show_connection_banner   # ← Phase 11.5
import json
import time
import uuid

user = require_login()
render_sidebar_user()

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }

    .page-title {
        font-size: 28px; font-weight: 800;
        color: #e94560; margin-bottom: 2px;
    }
    .page-sub {
        font-size: 13px; color: #606070;
        margin-bottom: 16px;
    }

    /* Chat bubbles */
    .user-bubble {
        background: #1e3a5f;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px; margin: 6px 0;
        color: #e8f4fd; font-size: 15px;
        max-width: 78%; float: right; clear: both;
    }
    .bot-bubble {
        background: #1a1a2e;
        border: 1px solid #2d2d4e;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px; margin: 6px 0;
        color: #e0e0e0; font-size: 15px;
        max-width: 85%; float: left; clear: both;
    }
    .clearfix::after { content:""; display:table; clear:both; }

    /* Product card */
    .rec-card {
        background: linear-gradient(135deg,#1a1a2e,#16213e);
        border: 1px solid #0f3460; border-radius:12px;
        padding:16px; margin:8px 0;
    }
    .rec-title {
        font-size:16px; font-weight:700; color:#e94560;
    }
    .rec-meta { font-size:13px; color:#a0a0b0; margin:4px 0; }

    /* Intent badge */
    .intent-badge {
        display:inline-block; padding:2px 10px;
        border-radius:12px; font-size:11px;
        font-weight:600; margin-left:6px;
    }

    /* Session item */
    .sess-label {
        font-size:13px; color:#c0c0d0;
        white-space:nowrap; overflow:hidden;
        text-overflow:ellipsis;
    }

    /* Welcome card */
    .welcome-card {
        background:#1a1a2e; border:1px solid #2d2d4e;
        border-radius:14px; padding:24px;
        text-align:center; margin-bottom:20px;
    }
</style>
""", unsafe_allow_html=True)

init_session()
show_connection_banner()              # ← Phase 11.5 (correct position: after init_session)


# ── Intent badge colors ───────────────────────────────────────────────────────
INTENT_COLORS = {
    "recommendation": ("#1a3a1a", "#4caf50"),
    "compare":        ("#1a2a3a", "#60a5fa"),
    "order":          ("#2a1a1a", "#f97316"),
    "track":          ("#2a2a1a", "#f59e0b"),
    "return":         ("#3a1a1a", "#ef4444"),
    "faq":            ("#1a1a3a", "#c084fc"),
}


def intent_badge(intent: str) -> str:
    bg, fg = INTENT_COLORS.get(intent, ("#1a1a2e", "#808090"))
    return (
        f'<span class="intent-badge" '
        f'style="background:{bg}; color:{fg};">'
        f'{intent.upper()}</span>'
    )


# ── Handle query ──────────────────────────────────────────────────────────────
def handle_query(query: str):
    if not query.strip():
        return

    st.session_state.messages.append({"role": "user", "content": query})

    with st.spinner("🤖 Analyzing your request..."):
        start   = time.time()
        result  = call_chat(query, st.session_state.session_id,
                            user_id=user["id"])
        elapsed = round(time.time() - start, 1)

    # ── Phase 11.5: catch API error before processing ─────────────────────────
    if show_api_error(result, "AI assistant"):
        st.session_state.messages.pop()   # remove the user message we just added
        return

    answer = result.get("answer", "Sorry, something went wrong.")
    intent = result.get("intent", "")

    if result.get("recommended_product"):
        st.session_state.last_product = result["recommended_product"]
    if result.get("order_id"):
        st.session_state.last_order_id = result["order_id"]
    if result.get("ranked_products"):
        st.session_state.ranked = result["ranked_products"]

    st.session_state.messages.append({
        "role":    "assistant",
        "content": answer,
        "intent":  intent,
        "elapsed": elapsed,
        "data":    result
    })

    saved = load_sessions()
    if st.session_state.session_id not in saved:
        save_session(st.session_state.session_id, label=query[:40])


# ── Render product card ───────────────────────────────────────────────────────
def render_rec_card(product: dict):
    pid = product.get("id")
    st.markdown(f"""
    <div class="rec-card">
        <div class="rec-title">{product.get("title","")}</div>
        <div class="rec-meta">✍️ {product.get("author","")}</div>
        <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;">
            <span style="background:#0f3460;color:#e94560;padding:3px 10px;
                         border-radius:20px;font-weight:700;font-size:13px;">
                ₹{product.get("price","")}
            </span>
            <span style="background:#1a3a1a;color:#4caf50;padding:3px 10px;
                         border-radius:20px;font-size:12px;">
                ⭐ {product.get("rating","")}/5
            </span>
            <span style="background:#2d1a3e;color:#c084fc;padding:3px 10px;
                         border-radius:20px;font-size:12px;">
                📂 {product.get("category","").title()}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("⚡ Buy Now", key=f"rec_buy_{pid}",
                     use_container_width=True, type="primary"):
            with st.spinner("Placing order..."):
                result = place_order(pid, st.session_state.session_id,
                                     user_id=user["id"])
            # ── Phase 11.5 ────────────────────────────────────────────────────
            if not show_api_error(result, "placing order"):
                if result.get("order_id"):
                    st.session_state.last_order_id = result["order_id"]
                    st.success(f"✅ Order placed! `{result['order_id']}`")
                    st.rerun()
    with col2:
        if st.button("📖 View Details", key=f"rec_detail_{pid}",
                     use_container_width=True):
            st.session_state.detail_product_id = pid
            st.switch_page("pages/4_Book_Detail.py")
    with col3:
        if st.button("🔁 Compare more", key=f"rec_compare_{pid}",
                     use_container_width=True):
            handle_query(
                f"Compare '{product.get('title','')}' with other "
                f"{product.get('category','')} books"
            )
            st.rerun()


# ── Render comparison table ───────────────────────────────────────────────────
def render_comparison(ranked: list):
    if not ranked:
        return
    st.markdown(f"**📊 {len(ranked)} Books Ranked & Scored**")
    for p in ranked:
        rank = p.get("rank", "")
        col_card, col_scores = st.columns([2, 3])
        with col_card:
            st.markdown(f"""
            <div class="rec-card">
                <div style="color:#606070;font-size:11px;">RANK #{rank}</div>
                <div class="rec-title">{p.get("title","")[:45]}</div>
                <div class="rec-meta">₹{p.get("price","")} &nbsp;|&nbsp;
                    ⭐{p.get("rating","")}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📖 Details", key=f"cmp_detail_{p.get('product_id')}",
                         use_container_width=True):
                st.session_state.detail_product_id = p.get("product_id")
                st.switch_page("pages/4_Book_Detail.py")
        with col_scores:
            metrics = [
                ("💰 Price Value",   p.get("price_value",       0)),
                ("🎓 Beginner",      p.get("beginner_friendly", 0)),
                ("📖 Content Depth", p.get("content_depth",     0)),
                ("⭐ Rating Score",  p.get("rating_score",      0)),
            ]
            m1, m2 = st.columns(2)
            for i, (label, val) in enumerate(metrics):
                col = m1 if i % 2 == 0 else m2
                with col:
                    st.metric(label, f"{val or 0}/10")


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🤖 AI Assistant")
    st.caption(f"Session: `{st.session_state.session_id[:14]}...`")

    st.divider()

    st.markdown("**⚡ Quick Prompts**")
    quick = [
        ("📘 ML under ₹1000",     "recommend a machine learning book under ₹1000"),
        ("🧠 Compare DL books",   "compare deep learning books"),
        ("🐍 Best Python book",   "what is the best python programming book?"),
        ("📊 Data science books", "suggest top data science books"),
        ("📦 My orders",          "show my orders"),
        ("🔁 Return last order",  "I want to return my last order"),
    ]
    for label, query in quick:
        if st.button(label, key=f"q_{label}", use_container_width=True):
            handle_query(query)
            st.rerun()

    st.divider()

    st.markdown("**⚙️ Sessions**")
    st.caption(f"💬 {len(get_history(st.session_state.session_id))} messages")

    if st.button("➕ New Session", use_container_width=True):
        if st.session_state.messages:
            first = next(
                (m["content"] for m in st.session_state.messages
                 if m["role"] == "user"), "Session"
            )
            save_session(st.session_state.session_id, label=first[:40])
        st.session_state.session_id    = str(uuid.uuid4())
        st.session_state.messages      = []
        st.session_state.last_product  = None
        st.session_state.last_order_id = None
        st.session_state.ranked        = []
        st.rerun()

    if st.button("🗑️ Clear Chat", use_container_width=True, type="secondary"):
        clear_history(st.session_state.session_id)
        st.session_state.messages = []
        st.rerun()

    st.divider()

    st.markdown("**🕓 Past Sessions**")
    saved = load_sessions()

    if not saved:
        st.caption("No saved sessions yet.")
    else:
        for sid, meta in list(saved.items()):
            is_current = sid == st.session_state.session_id
            label      = meta.get("label", "Untitled")[:26]
            created_at = meta.get("created_at", "")

            col_btn, col_del = st.columns([4, 1])
            with col_btn:
                prefix = "✅ " if is_current else "💬 "
                if st.button(f"{prefix}{label}...", key=f"sess_{sid}",
                             use_container_width=True, disabled=is_current):
                    st.session_state.session_id    = sid
                    st.session_state.last_product  = None
                    st.session_state.last_order_id = None
                    st.session_state.ranked        = []
                    history = get_history(sid, limit=50)
                    st.session_state.messages = [
                        {
                            "role":    h["role"],
                            "content": h["content"],
                            "intent":  h.get("intent", ""),
                            "elapsed": None,
                            "data":    {}
                        }
                        for h in history
                    ]
                    st.rerun()
            with col_del:
                if st.button("🗑", key=f"del_{sid}"):
                    delete_saved_session(sid)
                    if sid == st.session_state.session_id:
                        clear_history(sid)
                        st.session_state.messages = []
                    st.rerun()
            st.caption(f"🕐 {created_at}")

    st.divider()

    if st.button("🛍️ Browse Books", use_container_width=True):
        st.switch_page("pages/1_Browse.py")
    if st.button("📦 My Orders",    use_container_width=True):
        st.switch_page("pages/3_Orders.py")
    if st.button("🏠 Home",         use_container_width=True):
        st.switch_page("app.py")


# ════════════════════════════════════════════════════════════════════════════
# MAIN CHAT AREA
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="page-title">🤖 AI Book Assistant</div>',
            unsafe_allow_html=True)
st.markdown(
    '<div class="page-sub">'
    'Powered by LangGraph · 7 agents · NVIDIA + Groq LLMs'
    '</div>',
    unsafe_allow_html=True
)

if st.session_state.get("ai_prefill"):
    prefill = st.session_state.ai_prefill
    st.session_state.ai_prefill = None
    handle_query(prefill)
    st.rerun()

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome-card">
        <div style='font-size:44px;'>🤖</div>
        <div style='color:#e0e0e0;font-size:18px;font-weight:700;margin:8px 0;'>
            Your AI Book Expert
        </div>
        <div style='color:#606070;font-size:14px;'>
            I use 7 specialized agents to research, compare,
            and recommend books personally for you.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Try asking:**")
    c1, c2, c3 = st.columns(3)
    suggestions = [
        ("📘 ML under ₹1000",     "recommend a machine learning book under ₹1000"),
        ("🧠 Compare DL books",   "compare deep learning books"),
        ("🐍 Best Python book",   "what is the best python programming book?"),
        ("📊 Data science",       "top data science books for beginners"),
        ("📦 My orders",          "show my orders"),
        ("🔁 Return order",       "I want to return my last order"),
    ]
    for i, (label, query) in enumerate(suggestions):
        with [c1, c2, c3][i % 3]:
            if st.button(label, key=f"sug_{i}", use_container_width=True):
                handle_query(query)
                st.rerun()
    st.stop()

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="clearfix">'
            f'<div class="user-bubble">👤 {msg["content"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="clearfix">'
            f'<div class="bot-bubble">🤖 {msg["content"]}</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        data   = msg.get("data", {})
        intent = msg.get("intent", "")

        if data.get("recommended_product") and intent in (
            "recommendation", "compare", "order"
        ):
            with st.expander("📗 Recommended Book", expanded=True):
                render_rec_card(data["recommended_product"])

        if data.get("ranked_products") and len(data["ranked_products"]) > 1:
            with st.expander(
                f"📊 Full Comparison — {len(data['ranked_products'])} books",
                expanded=True
            ):
                render_comparison(data["ranked_products"])

        if data.get("order_id") and intent == "order":
            oid = data["order_id"]
            st.session_state.last_order_id = oid
            col1, col2 = st.columns(2)
            with col1:
                st.success(f"✅ Order placed: `{oid}`")
            with col2:
                if st.button("📦 Track It", key=f"track_{oid}"):
                    st.switch_page("pages/3_Orders.py")

        elapsed = msg.get("elapsed")
        if elapsed:
            badge = intent_badge(intent) if intent else ""
            st.markdown(
                f'<span style="color:#404060;font-size:11px;">'
                f'⏱️ {elapsed}s</span>{badge}',
                unsafe_allow_html=True
            )

st.divider()
user_input = st.chat_input(
    "Ask me anything — recommend, compare, order, track, return..."
)
if user_input:
    handle_query(user_input)
    st.rerun()