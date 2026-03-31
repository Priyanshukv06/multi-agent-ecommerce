import streamlit as st
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'frontend'))

st.set_page_config(
    page_title="Cart — AI Book Store",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.session import (require_login, render_sidebar_user,
                           init_session, cart_total,
                           remove_from_cart, clear_cart)
from utils.api     import place_order, get_product
from utils.error   import show_api_error, show_connection_banner    # ← ADDED
from auth.auth     import get_stock

user = require_login()
render_sidebar_user()
init_session()
show_connection_banner()                                             # ← ADDED

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .page-title {
        font-size: 32px; font-weight: 800; color: #e94560; margin-bottom: 4px;
    }
    .cart-item {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460; border-radius: 14px;
        padding: 16px; margin-bottom: 12px;
    }
    .item-title  { font-size: 16px; font-weight: 700; color: #e94560; }
    .item-author { font-size: 13px; color: #808090; margin: 4px 0; }
    .item-price  { font-size: 18px; font-weight: 800; color: #e94560; margin-top: 6px; }
    .summary-box {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 14px; padding: 20px;
        position: sticky; top: 20px;
    }
    .summary-title { font-size: 20px; font-weight: 700; color: #e0e0e0; }
    .summary-total { font-size: 28px; font-weight: 800; color: #e94560; margin: 12px 0; }
    .empty-state   { text-align: center; padding: 60px 20px; color: #404060; }
    .stock-warn    { color: #f59e0b; font-size: 12px; }
    .stock-ok      { color: #4caf50; font-size: 12px; }
    .success-card {
        background: #1a3a1a; border: 1px solid #4caf50;
        border-radius: 12px; padding: 16px; margin: 8px 0; color: #4caf50;
    }
</style>
""", unsafe_allow_html=True)


# ── Quantity helpers ──────────────────────────────────────────────────────────
def get_cart_quantities() -> dict:
    return st.session_state.get("cart_quantities", {})

def set_quantity(product_id: int, qty: int):
    if "cart_quantities" not in st.session_state:
        st.session_state["cart_quantities"] = {}
    st.session_state["cart_quantities"][product_id] = qty

def remove_quantity(product_id: int):
    qs = st.session_state.get("cart_quantities", {})
    qs.pop(product_id, None)
    st.session_state["cart_quantities"] = qs

def cart_total_with_qty() -> float:
    cart = st.session_state.get("cart", [])
    qtys = get_cart_quantities()
    return sum(
        p.get("price", 0) * qtys.get(p.get("id"), 1)
        for p in cart
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🛒 Cart")
    st.divider()

    cart = st.session_state.get("cart", [])
    st.metric("Items in Cart", len(cart))
    if cart:
        st.metric("Estimated Total", f"₹{cart_total_with_qty():,.0f}")

    st.divider()
    if st.button("🛍️ Browse More Books", use_container_width=True):
        st.switch_page("pages/1_Browse.py")
    if st.button("🤖 AI Assistant",      use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")    # ← FIXED
    if st.button("📦 My Orders",         use_container_width=True):
        st.switch_page("pages/3_Orders.py")
    if st.button("🏠 Home",              use_container_width=True):
        st.switch_page("app.py")


# ── Checkout Success State ────────────────────────────────────────────────────
if st.session_state.get("checkout_results"):
    results = st.session_state.checkout_results

    st.markdown('<div class="page-title">🎉 Order Placed!</div>',
                unsafe_allow_html=True)
    st.markdown("")

    success_count = sum(1 for _, r in results if r.get("order_id"))
    fail_count    = len(results) - success_count

    if success_count:
        st.success(f"✅ {success_count} order(s) placed successfully!")
    if fail_count:
        st.warning(f"⚠️ {fail_count} item(s) could not be ordered.")

    for product, result in results:
        if result.get("order_id"):
            st.markdown(f"""
            <div class="success-card">
                <b>{product['title'][:55]}</b><br>
                🆔 Order ID: <code style="color:#c084fc">{result['order_id']}</code>
                &nbsp;|&nbsp; ₹{product.get('price', 0):,.0f}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#3a1a1a; border:1px solid #f87171;
                        border-radius:12px; padding:14px; margin:6px 0; color:#f87171;">
                ❌ {product['title'][:55]} — {result.get('error','Failed')}
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📦 Track Orders", type="primary", use_container_width=True):
            st.session_state.checkout_results = None
            st.switch_page("pages/3_Orders.py")
    with c2:
        if st.button("🛍️ Browse More", use_container_width=True):
            st.session_state.checkout_results = None
            st.switch_page("pages/1_Browse.py")
    with c3:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.checkout_results = None
            st.switch_page("app.py")
    st.stop()


# ── Main Cart View ────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">🛒 Your Cart</div>', unsafe_allow_html=True)

cart = st.session_state.get("cart", [])

if not cart:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size:56px;">🛒</div>
        <div style="font-size:22px; margin:12px 0; color:#e0e0e0;">Your cart is empty</div>
        <div style="font-size:14px;">Browse books and add them to your cart!</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🛍️ Browse Books", type="primary"):
        st.switch_page("pages/1_Browse.py")
    st.stop()

col_items, col_summary = st.columns([3, 1])

with col_items:
    st.markdown(f"**{len(cart)} item(s) in your cart**")
    st.markdown("")

    for product in cart:
        pid   = product.get("id")
        stock = get_stock(pid)
        qtys  = get_cart_quantities()
        qty   = qtys.get(pid, 1)

        with st.container():
            st.markdown('<div class="cart-item">', unsafe_allow_html=True)

            row1, row_remove = st.columns([5, 1])
            with row1:
                st.markdown(
                    f'<div class="item-title">{product.get("title","")}</div>'
                    f'<div class="item-author">✍️ {product.get("author","")}'
                    f' &nbsp;|&nbsp; 📂 {product.get("category","").title()}'
                    f' &nbsp;|&nbsp; ⭐ {product.get("rating","")}/5</div>',
                    unsafe_allow_html=True
                )
            with row_remove:
                if st.button("🗑️", key=f"rm_{pid}", help="Remove from cart"):
                    remove_from_cart(pid)
                    remove_quantity(pid)
                    st.rerun()

            price_col, qty_col, subtotal_col = st.columns([2, 2, 2])

            with price_col:
                st.markdown(
                    f'<div class="item-price">₹{product.get("price",0):,.0f}</div>'
                    f'<div style="font-size:11px;color:#606070;">per book</div>',
                    unsafe_allow_html=True
                )

            with qty_col:
                max_qty = min(stock, 10) if stock > 0 else 1
                new_qty = st.number_input(
                    "Qty",
                    min_value=1,
                    max_value=max_qty,
                    value=min(qty, max_qty),
                    step=1,
                    key=f"qty_{pid}",
                    label_visibility="collapsed"
                )
                if new_qty != qty:
                    set_quantity(pid, new_qty)
                    st.rerun()

                if stock == 0:
                    st.markdown(
                        '<div class="stock-warn">⚠️ Out of stock</div>',
                        unsafe_allow_html=True
                    )
                elif stock <= 5:
                    st.markdown(
                        f'<div class="stock-warn">⚠️ Only {stock} left</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="stock-ok">✅ {stock} in stock</div>',
                        unsafe_allow_html=True
                    )

            with subtotal_col:
                subtotal = product.get("price", 0) * new_qty
                st.markdown(
                    f'<div style="font-size:16px; font-weight:700; '
                    f'color:#c084fc; margin-top:6px;">₹{subtotal:,.0f}</div>'
                    f'<div style="font-size:11px;color:#606070;">subtotal</div>',
                    unsafe_allow_html=True
                )

            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("")

    st.markdown("")
    if st.button("🗑️ Clear Entire Cart", use_container_width=True, type="secondary"):
        clear_cart()
        st.session_state["cart_quantities"] = {}
        st.rerun()


# ── Order Summary ─────────────────────────────────────────────────────────────
with col_summary:
    qtys  = get_cart_quantities()
    total = cart_total_with_qty()

    st.markdown("""
    <div class="summary-box">
        <div class="summary-title">🧾 Order Summary</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")

    for product in cart:
        pid = product.get("id")
        qty = qtys.get(pid, 1)
        st.markdown(
            f'<div style="display:flex; justify-content:space-between; '
            f'font-size:13px; color:#a0a0b0; margin:4px 0;">'
            f'<span>{product.get("title","")[:22]}... x{qty}</span>'
            f'<span>₹{product.get("price",0)*qty:,.0f}</span></div>',
            unsafe_allow_html=True
        )

    st.divider()
    st.markdown(
        f'<div style="display:flex; justify-content:space-between; '
        f'font-size:18px; font-weight:800; color:#e0e0e0;">'
        f'<span>Total</span>'
        f'<span style="color:#e94560;">₹{total:,.0f}</span></div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    out_of_stock = []
    for product in cart:
        pid   = product.get("id")
        qty   = qtys.get(pid, 1)
        stock = get_stock(pid)
        if stock < qty:
            out_of_stock.append(product.get("title", "")[:30])

    if out_of_stock:
        st.warning(
            "⚠️ Some items have insufficient stock:\n" +
            "\n".join(f"• {t}" for t in out_of_stock)
        )
        st.button("🛒 Checkout", use_container_width=True,
                  type="primary", disabled=True)
    else:
        if st.button("🛒 Place Order", use_container_width=True, type="primary"):
            results  = []
            progress = st.progress(0)

            for i, product in enumerate(cart):
                pid = product.get("id")
                qty = qtys.get(pid, 1)
                last_result = {"error": "Not placed"}

                # ── FIXED: loop qty times since place_order has no quantity param
                for _ in range(qty):
                    with st.spinner(f"Ordering {product.get('title','')[:30]}..."):
                        last_result = place_order(
                            pid,
                            st.session_state.get("session_id", "default"),
                            user_id=user["id"]
                        )
                    # ── ADDED: error check per order ──────────────────────────
                    if show_api_error(last_result, f"ordering {product.get('title','')[:20]}"):
                        break

                results.append((product, last_result))
                progress.progress((i + 1) / len(cart))

            st.session_state["checkout_results"] = results
            clear_cart()
            st.session_state["cart_quantities"] = {}
            st.rerun()

    st.markdown("")
    if st.button("🤖 Need help choosing?", use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")    # ← FIXED