import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.api     import place_order, get_product
from utils.session import (init_session, cart_total, clear_cart,
                           remove_from_cart, in_cart)

st.set_page_config(
    page_title="Cart — AI Book Store",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .page-title {
        font-size: 32px; font-weight: 800;
        color: #e94560; margin-bottom: 4px;
    }
    .cart-item {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460; border-radius: 12px;
        padding: 16px; margin-bottom: 10px;
    }
    .item-title {
        font-size: 16px; font-weight: 700; color: #e0e0e0;
    }
    .item-author { font-size: 13px; color: #808090; margin: 3px 0; }
    .item-price {
        font-size: 20px; font-weight: 800; color: #e94560;
    }
    .summary-box {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 14px; padding: 20px;
        position: sticky; top: 20px;
    }
    .summary-row {
        display: flex; justify-content: space-between;
        padding: 8px 0; border-bottom: 1px solid #2d2d4e;
        color: #c0c0d0; font-size: 14px;
    }
    .summary-total {
        display: flex; justify-content: space-between;
        padding: 12px 0; color: #e94560;
        font-size: 20px; font-weight: 800;
    }
    .empty-cart {
        text-align: center; padding: 80px 20px; color: #404060;
    }
    .success-card {
        background: #1a3a1a; border: 1px solid #4caf50;
        border-radius: 12px; padding: 20px;
        text-align: center; margin: 12px 0;
    }
    .savings-badge {
        background: #1a3a1a; color: #4caf50;
        padding: 3px 10px; border-radius: 20px;
        font-size: 12px; font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

init_session()


# ── Checkout complete screen ──────────────────────────────────────────────────
if st.session_state.get("checkout_complete"):
    orders = st.session_state.checkout_complete

    st.markdown("""
    <div style='text-align:center; padding:20px 0;'>
        <div style='font-size:56px;'>🎉</div>
        <div style='font-size:28px; font-weight:800;
                    color:#4caf50; margin:8px 0;'>
            Order(s) Placed Successfully!
        </div>
        <div style='color:#808090; font-size:15px;'>
            Your books are being packed and will be delivered soon.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 📦 Your Orders")
    for product, result in orders:
        if result.get("order_id"):
            st.markdown(f"""
            <div class="success-card">
                <div style='font-size:18px; font-weight:700;
                            color:#e0e0e0;'>{product['title']}</div>
                <div style='color:#808090; font-size:13px;
                            margin:4px 0;'>by {product['author']}</div>
                <div style='color:#4caf50; font-size:20px;
                            font-weight:700; margin:8px 0;'>
                    ✅ Order Confirmed
                </div>
                <div style='color:#c084fc; font-family:monospace;
                            font-size:14px;'>
                    {result['order_id']}
                </div>
                <div style='color:#808090; font-size:12px; margin-top:4px;'>
                    🚚 Estimated delivery: {result.get('message','3-5 business days')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📦 Track Orders",
                     use_container_width=True, type="primary"):
            st.session_state.checkout_complete = None
            st.switch_page("pages/3_Orders.py")
    with c2:
        if st.button("🛍️ Continue Shopping", use_container_width=True):
            st.session_state.checkout_complete = None
            st.switch_page("pages/1_Browse.py")
    with c3:
        if st.button("🤖 Ask AI for next book", use_container_width=True):
            st.session_state.checkout_complete = None
            st.session_state.ai_prefill = (
                "I just ordered some books. What should I read next?"
            )
            st.switch_page("pages/2_AI_Assistant.py")
    st.stop()


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🛒 Cart")
    cart  = st.session_state.get("cart", [])
    total = cart_total()
    st.caption(f"{len(cart)} item(s) · ₹{total:.0f} total")
    st.divider()
    if st.button("🛍️ Browse More Books",  use_container_width=True):
        st.switch_page("pages/1_Browse.py")
    if st.button("🤖 Ask AI to help",     use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")
    if st.button("📦 My Orders",          use_container_width=True):
        st.switch_page("pages/3_Orders.py")
    if st.button("🏠 Home",               use_container_width=True):
        st.switch_page("app.py")


# ════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="page-title">🛒 Your Cart</div>',
            unsafe_allow_html=True)

cart  = st.session_state.get("cart", [])
total = cart_total()

# ── Empty cart ────────────────────────────────────────────────────────────────
if not cart:
    st.markdown("""
    <div class="empty-cart">
        <div style='font-size:64px;'>🛒</div>
        <div style='font-size:22px; font-weight:700;
                    color:#e0e0e0; margin:12px 0 8px;'>
            Your cart is empty
        </div>
        <div style='font-size:14px; color:#606070;'>
            Browse books and add them to your cart!
        </div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛍️ Browse Books",
                     use_container_width=True, type="primary"):
            st.switch_page("pages/1_Browse.py")
    with c2:
        if st.button("🤖 Ask AI to recommend",
                     use_container_width=True):
            st.switch_page("pages/2_AI_Assistant.py")
    st.stop()


# ── Two column layout — Items | Summary ──────────────────────────────────────
col_items, col_summary = st.columns([3, 2])

with col_items:
    st.markdown(f"### 📚 {len(cart)} Book(s) in Cart")

    # Clear all button
    if st.button("🗑️ Clear All", type="secondary"):
        clear_cart()
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Cart items ────────────────────────────────────────────────────────
    for i, book in enumerate(cart):
        pid = book["id"]

        with st.container():
            st.markdown(f"""
            <div class="cart-item">
                <div class="item-title">{book["title"]}</div>
                <div class="item-author">✍️ {book["author"]}</div>
                <div style='margin-top:6px; display:flex;
                            gap:6px; align-items:center;'>
                    <span style='background:#2d1a3e;color:#c084fc;
                                 padding:2px 8px;border-radius:12px;
                                 font-size:12px;'>
                        📂 {book["category"].title()}
                    </span>
                    <span style='background:#1a3a1a;color:#4caf50;
                                 padding:2px 8px;border-radius:12px;
                                 font-size:12px;'>
                        ⭐ {book["rating"]}/5
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_price, col_detail, col_remove = st.columns([2, 2, 1])
            with col_price:
                st.markdown(
                    f'<div class="item-price">₹{book["price"]}</div>',
                    unsafe_allow_html=True
                )
            with col_detail:
                if st.button("📖 Details", key=f"cart_detail_{pid}",
                             use_container_width=True):
                    st.session_state.detail_product_id = pid
                    st.switch_page("pages/4_Book_Detail.py")
            with col_remove:
                if st.button("🗑", key=f"cart_remove_{pid}",
                             use_container_width=True):
                    remove_from_cart(pid)
                    st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)


with col_summary:
    # ── Order Summary Box ─────────────────────────────────────────────────
    st.markdown("### 🧾 Order Summary")

    st.markdown(f"""
    <div class="summary-box">
        <div class="summary-row">
            <span>Items ({len(cart)})</span>
            <span>₹{total:.0f}</span>
        </div>
        <div class="summary-row">
            <span>Delivery</span>
            <span style="color:#4caf50;">FREE</span>
        </div>
        <div class="summary-row">
            <span>Tax</span>
            <span>Included</span>
        </div>
        <div class="summary-total">
            <span>Total</span>
            <span>₹{total:.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Checkout button ───────────────────────────────────────────────────
    if st.button("✅ Place Order(s)", use_container_width=True,
                 type="primary", key="checkout_btn"):
        progress = st.progress(0)
        results  = []

        for i, book in enumerate(cart):
            with st.spinner(f"Ordering '{book['title'][:25]}'..."):
                result = place_order(book["id"], st.session_state.session_id)
                results.append((book, result))
                if result.get("order_id"):
                    st.session_state.last_order_id = result["order_id"]
            progress.progress((i + 1) / len(cart))

        clear_cart()
        st.session_state.checkout_complete = results
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Coupon placeholder ────────────────────────────────────────────────
    with st.expander("🏷️ Have a coupon?"):
        coupon = st.text_input("Enter coupon code",
                               placeholder="SAVE10",
                               label_visibility="collapsed")
        if st.button("Apply", use_container_width=True):
            st.info("🚧 Coupons coming soon!")

    # ── Ask AI ────────────────────────────────────────────────────────────
    st.divider()
    st.caption("Not sure about your cart?")
    if st.button("🤖 Ask AI to review my cart",
                 use_container_width=True):
        titles = ", ".join([b["title"][:20] for b in cart])
        st.session_state.ai_prefill = (
            f"I have these books in my cart: {titles}. "
            f"Are these good choices? What do you think?"
        )
        st.switch_page("pages/2_AI_Assistant.py")