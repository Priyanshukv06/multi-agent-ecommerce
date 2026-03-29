import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.api     import get_product, get_products, place_order
from utils.session import init_session, add_to_cart, in_cart, remove_from_cart

st.set_page_config(
    page_title="Book Detail — AI Book Store",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }

    .detail-title {
        font-size: 32px; font-weight: 800;
        color: #e0e0e0; line-height: 1.3;
        margin-bottom: 8px;
    }
    .detail-author {
        font-size: 16px; color: #808090;
        margin-bottom: 16px;
    }
    .badge {
        display: inline-block;
        padding: 4px 14px; border-radius: 20px;
        font-size: 14px; font-weight: 600;
        margin-right: 6px; margin-bottom: 8px;
    }
    .badge-price   { background:#0f3460; color:#e94560; }
    .badge-rating  { background:#1a3a1a; color:#4caf50; }
    .badge-cat     { background:#2d1a3e; color:#c084fc; }

    .desc-box {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 12px; padding: 20px;
        color: #c0c0d0; font-size: 15px;
        line-height: 1.7; margin: 16px 0;
    }
    .review-card {
        background: #16213e; border-left: 3px solid #e94560;
        border-radius: 8px; padding: 12px 16px;
        margin: 8px 0; color: #c0c0d0;
        font-size: 14px; font-style: italic;
    }
    .similar-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460; border-radius: 12px;
        padding: 14px; margin: 6px 0; cursor: pointer;
    }
    .similar-title {
        font-size: 14px; font-weight: 700;
        color: #e94560; min-height: 38px;
    }
    .action-box {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 14px; padding: 20px;
        position: sticky; top: 20px;
    }
    .price-large {
        font-size: 36px; font-weight: 800;
        color: #e94560; margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

init_session()

# ── Guard — must have a product_id in session ─────────────────────────────────
product_id = st.session_state.get("detail_product_id")

if not product_id:
    st.warning("No book selected.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛍️ Browse Books", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Browse.py")
    with col2:
        if st.button("🏠 Home", use_container_width=True):
            st.switch_page("app.py")
    st.stop()

# ── Load product ──────────────────────────────────────────────────────────────
with st.spinner("Loading book details..."):
    book = get_product(product_id)

if not book or book.get("detail"):
    st.error("Book not found.")
    if st.button("← Back to Browse"):
        st.switch_page("pages/1_Browse.py")
    st.stop()

# ── Breadcrumb ────────────────────────────────────────────────────────────────
b1, b2, b3 = st.columns([1, 1, 6])
with b1:
    if st.button("🏠 Home"):
        st.switch_page("app.py")
with b2:
    if st.button("🛍️ Browse"):
        st.switch_page("pages/1_Browse.py")

st.divider()

# ════════════════════════════════════════════════════════════════════════════
# MAIN LAYOUT — Left: Details | Right: Buy Box
# ════════════════════════════════════════════════════════════════════════════
col_detail, col_action = st.columns([3, 1])

with col_detail:

    # ── Title + Author ────────────────────────────────────────────────────────
    st.markdown(
        f'<div class="detail-title">{book["title"]}</div>',
        unsafe_allow_html=True
    )
    st.markdown(
        f'<div class="detail-author">by {book["author"]}</div>',
        unsafe_allow_html=True
    )

    # ── Badges ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <span class="badge badge-price">₹{book["price"]}</span>
    <span class="badge badge-rating">⭐ {book["rating"]}/5</span>
    <span class="badge badge-cat">📂 {book["category"].title()}</span>
    """, unsafe_allow_html=True)

    # ── Tabs: Description / Reviews / AI Analysis ─────────────────────────────
    tab_desc, tab_reviews, tab_ai = st.tabs([
        "📄 Description", "💬 Reviews", "🤖 AI Analysis"
    ])

    with tab_desc:
        st.markdown(
            f'<div class="desc-box">{book.get("description","No description available.")}</div>',
            unsafe_allow_html=True
        )

        # Key highlights
        st.markdown("### 📌 Key Highlights")
        highlights = [
            f"📚 **Category:** {book['category'].title()}",
            f"⭐ **Rating:** {book['rating']}/5",
            f"💰 **Price:** ₹{book['price']}",
            f"✍️ **Author:** {book['author']}",
        ]
        for h in highlights:
            st.markdown(f"- {h}")

    with tab_reviews:
        reviews = book.get("reviews", [])
        if not reviews:
            st.info("No reviews available for this book.")
        else:
            st.markdown(f"**{len(reviews)} Reader Reviews**")
            for i, review in enumerate(reviews, 1):
                st.markdown(
                    f'<div class="review-card">'
                    f'<span style="color:#e94560; font-size:12px; '
                    f'font-style:normal;">Reader {i}</span><br>'
                    f'"{review}"</div>',
                    unsafe_allow_html=True
                )

    with tab_ai:
        st.markdown("""
        <div style='background:#1a1a2e; border:1px solid #0f3460;
                    border-radius:12px; padding:20px; text-align:center;'>
            <div style='font-size:32px; margin-bottom:8px;'>🤖</div>
            <div style='color:#e0e0e0; font-size:16px; font-weight:700;'>
                Want AI to analyze this book?
            </div>
            <div style='color:#808090; font-size:14px; margin-top:8px;'>
                Our 7-agent system will research, compare,
                and give you a personalized recommendation.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        ai_options = [
            ("🔍 Full Analysis",
             f"Give me a detailed analysis of '{book['title']}' by {book['author']}"),
            ("⚖️ Compare with similar",
             f"Compare '{book['title']}' with similar {book['category']} books"),
            ("🎯 Is it right for me?",
             f"Is '{book['title']}' good for a beginner? What level is it?"),
            ("📚 What to read next",
             f"I want to read '{book['title']}'. What should I read after?"),
        ]

        for label, query in ai_options:
            if st.button(label, use_container_width=True):
                st.session_state.ai_prefill = query
                st.switch_page("pages/2_AI_Assistant.py")


# ── Similar Books ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📚 Similar Books")

with st.spinner("Finding similar books..."):
    similar = get_products(category=book["category"], limit=6)
    similar = [b for b in similar if b["id"] != book["id"]][:4]

if similar:
    sim_cols = st.columns(len(similar))
    for col, sim in zip(sim_cols, similar):
        with col:
            st.markdown(f"""
            <div class="similar-card">
                <div class="similar-title">{sim["title"][:40]}</div>
                <div style="font-size:12px; color:#808090; margin:4px 0;">
                    {sim["author"][:25]}
                </div>
                <div style="margin-top:6px;">
                    <span style="color:#e94560; font-weight:700;">
                        ₹{sim["price"]}
                    </span>
                    &nbsp;
                    <span style="color:#4caf50; font-size:12px;">
                        ⭐{sim["rating"]}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("View Details", key=f"sim_{sim['id']}",
                         use_container_width=True):
                st.session_state.detail_product_id = sim["id"]
                st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# RIGHT COLUMN — Buy Box (sticky action panel)
# ════════════════════════════════════════════════════════════════════════════
with col_action:
    st.markdown(f"""
    <div class="action-box">
        <div style="color:#808090; font-size:13px;">Price</div>
        <div class="price-large">₹{book["price"]}</div>
        <div style="color:#4caf50; font-size:14px; margin-bottom:16px;">
            ⭐ {book["rating"]}/5 rating
        </div>
        <div style="color:#4caf50; font-size:13px; margin-bottom:12px;">
            ✅ In Stock &nbsp;|&nbsp; 🚚 Free Delivery
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Buy Now ────────────────────────────────────────────────────────────
    if st.button("⚡ Buy Now", use_container_width=True,
                 type="primary", key="detail_buy"):
        with st.spinner("Placing order..."):
            result = place_order(book["id"], st.session_state.session_id)
        if result.get("order_id"):
            st.session_state.last_order_id = result["order_id"]
            st.success(
                f"✅ Order placed!\n\n"
                f"**Order ID:** `{result['order_id']}`"
            )
            if st.button("📦 Track Order", use_container_width=True):
                st.switch_page("pages/3_Orders.py")
        else:
            st.error("Order failed. Please try again.")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Add to Cart ────────────────────────────────────────────────────────
    if in_cart(book["id"]):
        if st.button("🛒 Remove from Cart", use_container_width=True,
                     key="detail_cart"):
            remove_from_cart(book["id"])
            st.rerun()
        st.success("✅ In your cart")
    else:
        if st.button("➕ Add to Cart", use_container_width=True,
                     key="detail_cart"):
            add_to_cart(book)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Ask AI ─────────────────────────────────────────────────────────────
    st.markdown("---")
    st.caption("Not sure? Let AI help:")
    if st.button("🤖 Ask AI Assistant", use_container_width=True,
                 key="detail_ai"):
        st.session_state.ai_prefill = (
            f"Should I buy '{book['title']}' by {book['author']}? "
            f"Compare it with similar books and give me a recommendation."
        )
        st.switch_page("pages/2_AI_Assistant.py")