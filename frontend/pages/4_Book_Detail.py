import streamlit as st
import sys
import os
import json

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'frontend'))

st.set_page_config(
    page_title="Book Detail — AI Book Store",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.api     import get_product, get_products, place_order
from utils.session import (init_session, add_to_cart, remove_from_cart,
                           in_cart, require_login, render_sidebar_user)
from auth.auth     import get_stock

user = require_login()
render_sidebar_user()
init_session()

PLACEHOLDER = "https://covers.openlibrary.org/b/isbn/0000000000-M.jpg"

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .detail-title {
        font-size: 28px; font-weight: 800;
        color: #e0e0e0; line-height: 1.3; margin-bottom: 8px;
    }
    .detail-author { font-size: 15px; color: #808090; margin-bottom: 14px; }
    .badge {
        display: inline-block; padding: 4px 14px;
        border-radius: 20px; font-size: 13px;
        font-weight: 600; margin-right: 6px; margin-bottom: 8px;
    }
    .badge-price  { background: #0f3460; color: #e94560; }
    .badge-rating { background: #1a3a1a; color: #4caf50; }
    .badge-cat    { background: #2d1a3e; color: #c084fc; }
    .desc-box {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 12px; padding: 20px;
        color: #c0c0d0; font-size: 15px;
        line-height: 1.7; margin: 14px 0;
    }
    .review-card {
        background: #16213e; border-left: 3px solid #e94560;
        border-radius: 8px; padding: 12px 16px; margin: 8px 0;
        color: #c0c0d0; font-size: 14px; font-style: italic;
    }
    .similar-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460; border-radius: 12px;
        padding: 10px; margin: 4px 0; text-align: center;
    }
    .action-box {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 14px; padding: 20px;
        position: sticky; top: 20px;
    }
    .price-large  { font-size: 34px; font-weight: 800; color: #e94560; margin: 8px 0; }
    .stock-ok     { color: #4caf50; font-size: 13px; }
    .stock-warn   { color: #f59e0b; font-size: 13px; }
    .stock-none   { color: #ef4444; font-size: 13px; }
</style>
""", unsafe_allow_html=True)


# ── Guard ─────────────────────────────────────────────────────────────────────
product_id = st.session_state.get("detail_product_id")
if not product_id:
    st.warning("⚠️ No book selected.")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛍️ Browse Books", type="primary",
                     use_container_width=True):
            st.switch_page("pages/1_Browse.py")
    with c2:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")
    st.stop()


# ── Load product ──────────────────────────────────────────────────────────────
with st.spinner("Loading book details..."):
    book = get_product(product_id)

if not book or book.get("error"):
    st.error("❌ Book not found.")
    if st.button("← Back to Browse"):
        st.switch_page("pages/1_Browse.py")
    st.stop()

pid   = book.get("id")
stock = get_stock(pid)
cover = book.get("cover_url") or PLACEHOLDER

raw_reviews = book.get("reviews", [])
if isinstance(raw_reviews, str):
    try:    reviews = json.loads(raw_reviews)
    except: reviews = [raw_reviews] if raw_reviews else []
else:
    reviews = raw_reviews if isinstance(raw_reviews, list) else []


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📖 Book Detail")
    st.divider()
    if st.button("← Back to Browse", use_container_width=True):
        st.switch_page("pages/1_Browse.py")
    if st.button("🤖 AI Assistant", use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")
    if st.button("📦 My Orders", use_container_width=True):
        st.switch_page("pages/3_Orders.py")
    if st.button("🛒 Cart", use_container_width=True):
        st.switch_page("pages/5_Cart.py")
    if st.button("🏠 Home", use_container_width=True):
        st.switch_page("app.py")


# ── Breadcrumb ────────────────────────────────────────────────────────────────
b1, b2, _ = st.columns([1, 1, 8])
with b1:
    if st.button("🏠 Home"):    st.switch_page("app.py")
with b2:
    if st.button("🛍️ Browse"): st.switch_page("pages/1_Browse.py")
st.divider()


# ── Main Layout ───────────────────────────────────────────────────────────────
col_cover, col_detail, col_action = st.columns([1, 3, 1])


# ── Cover ─────────────────────────────────────────────────────────────────────
with col_cover:
    try:
        st.image(cover, use_container_width=True)
    except Exception:
        st.image(PLACEHOLDER, use_container_width=True)


# ── Detail ────────────────────────────────────────────────────────────────────
with col_detail:
    st.markdown(
        f'<div class="detail-title">{book.get("title","")}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="detail-author">by {book.get("author","")}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<span class="badge badge-price">₹{book.get("price","")}</span>'
        f'<span class="badge badge-rating">⭐ {book.get("rating","")}/5</span>'
        f'<span class="badge badge-cat">📂 {book.get("category","").title()}</span>',
        unsafe_allow_html=True
    )
    st.markdown("")

    tab_desc, tab_reviews, tab_ai = st.tabs(
        ["📄 Description", "💬 Reviews", "🤖 AI Analysis"]
    )

    with tab_desc:
        st.markdown(
            f'<div class="desc-box">'
            f'{book.get("description","No description available.")}'
            f'</div>',
            unsafe_allow_html=True
        )
        st.markdown("**Key Highlights**")
        for h in [
            f"📂 Category: {book.get('category','').title()}",
            f"⭐ Rating: {book.get('rating','')}/5",
            f"💰 Price: ₹{book.get('price','')}",
            f"✍️ Author: {book.get('author','')}",
        ]:
            st.markdown(f"- {h}")

    with tab_reviews:
        if not reviews:
            st.info("No reviews available for this book.")
        else:
            st.markdown(f"**{len(reviews)} Reader Reviews**")
            for i, review in enumerate(reviews, 1):
                st.markdown(
                    f'<div class="review-card">'
                    f'<span style="color:#e94560; font-size:12px;'
                    f'font-style:normal;">Reader {i}</span><br>'
                    f'{review}</div>',
                    unsafe_allow_html=True
                )

    with tab_ai:
        st.markdown("""
        <div style="background:#1a1a2e; border:1px solid #0f3460;
                    border-radius:12px; padding:24px; text-align:center;">
            <div style="font-size:36px; margin-bottom:8px;">🤖</div>
            <div style="color:#e0e0e0; font-size:16px; font-weight:700;">
                Want AI to analyze this book?
            </div>
            <div style="color:#808090; font-size:14px; margin-top:8px;">
                Our 7-agent system will research, compare, and give you
                a personalized recommendation.
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("")

        ai_options = [
            ("🔍 Full Analysis",
             f"Give me a detailed analysis of '{book.get('title','')}' "
             f"by {book.get('author','')}"),
            ("⚖️ Compare with similar",
             f"Compare '{book.get('title','')}' with similar "
             f"{book.get('category','')} books"),
            ("🎯 Is it right for me?",
             f"Is '{book.get('title','')}' good for a beginner? "
             f"What level is it?"),
            ("📚 What to read next",
             f"I just read '{book.get('title','')}'. "
             f"What should I read next?"),
        ]
        c1, c2 = st.columns(2)
        for i, (label, query) in enumerate(ai_options):
            with (c1 if i % 2 == 0 else c2):
                if st.button(label, key=f"ai_opt_{i}",
                             width='stretch'):           # ← FIXED
                    st.session_state.ai_prefill = query
                    st.switch_page("pages/2_AI_Assistant.py")    # ← FIXED

    st.markdown("---")
    st.markdown("### 📚 Similar Books")

    with st.spinner("Finding similar books..."):
        similar = get_products(category=book.get("category"), limit=6)
        similar = [b for b in similar if b.get("id") != pid][:4]

    if similar:
        sim_cols = st.columns(4)
        for col, sim in zip(sim_cols, similar):
            sim_cover = sim.get("cover_url") or PLACEHOLDER
            with col:
                try:
                    st.image(sim_cover, use_container_width=True)
                except Exception:
                    st.image(PLACEHOLDER, use_container_width=True)

                st.markdown(f"""
                <div class="similar-card">
                    <div style="font-size:12px; font-weight:700;
                                color:#e94560; min-height:32px;">
                        {sim.get('title','')[:35]}
                    </div>
                    <div style="font-size:11px; color:#808090; margin:3px 0;">
                        {sim.get('author','')[:20]}
                    </div>
                    <div style="color:#e94560; font-weight:700;
                                font-size:13px; margin-top:4px;">
                        ₹{sim.get('price','')}
                        <span style="color:#4caf50; font-size:11px;">
                            ⭐{sim.get('rating','')}
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("📖 View", key=f"sim_{sim.get('id')}",
                             use_container_width=True):
                    st.session_state.detail_product_id = sim.get("id")
                    st.rerun()
    else:
        st.caption("No similar books found.")


# ── Buy Box ───────────────────────────────────────────────────────────────────
with col_action:
    st.markdown('<div class="action-box">', unsafe_allow_html=True)

    st.markdown(
        f'<div style="color:#808090;font-size:13px;">Price</div>'
        f'<div class="price-large">₹{book.get("price","")}</div>'
        f'<div style="color:#4caf50;font-size:14px;margin-bottom:12px;">'
        f'⭐ {book.get("rating","")}/5 rating</div>',
        unsafe_allow_html=True
    )

    if stock == 0:
        st.markdown('<div class="stock-none">❌ Out of stock</div>',
                    unsafe_allow_html=True)
    elif stock <= 5:
        st.markdown(f'<div class="stock-warn">⚠️ Only {stock} left!</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="stock-ok">✅ {stock} in stock</div>',
                    unsafe_allow_html=True)

    st.markdown(
        '<div style="color:#4caf50;font-size:13px;margin-bottom:14px;">'
        '🚚 Free Delivery</div>',
        unsafe_allow_html=True
    )

    if stock > 0:
        if st.button("⚡ Buy Now", use_container_width=True,
                     type="primary", key="detail_buy"):
            with st.spinner("Placing order..."):
                result = place_order(
                    pid,
                    st.session_state.get("session_id", "default"),
                    user_id=user["id"]
                )
            if result.get("order_id"):
                st.success(f"✅ Order placed!\n\n`{result['order_id']}`")
                st.session_state.last_order_id = result["order_id"]
                if st.button("📦 Track", use_container_width=True):
                    st.switch_page("pages/3_Orders.py")
            else:
                st.error(f"Failed: {result.get('error','Unknown')}")
    else:
        st.button("⚡ Buy Now", use_container_width=True,
                  type="primary", key="detail_buy_dis", disabled=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if in_cart(pid):
        if st.button("✅ Remove from Cart", use_container_width=True,
                     key="detail_cart"):
            remove_from_cart(pid)
            st.rerun()
        st.success("📦 In your cart")
    else:
        if stock > 0:
            if st.button("🛒 Add to Cart", use_container_width=True,
                         key="detail_cart"):
                add_to_cart(book)
                st.rerun()
        else:
            st.button("🛒 Out of Stock", use_container_width=True,
                      key="detail_cart_dis", disabled=True)

    st.markdown("---")
    st.caption("Not sure? Let AI help.")
    if st.button("🤖 Ask AI", use_container_width=True,
                 key="detail_ai"):
        st.session_state.ai_prefill = (
            f"Should I buy '{book.get('title','')}' "
            f"by {book.get('author','')}? "
            f"Compare with similar books."
        )
        st.switch_page("pages/2_AI_Assistant.py")                    # ← FIXED

    st.markdown('</div>', unsafe_allow_html=True)