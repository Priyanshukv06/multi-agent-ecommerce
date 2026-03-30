import streamlit as st
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'frontend'))

st.set_page_config(
    page_title="Browse Books — AI Book Store",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.api     import get_products, get_categories, get_price_range, place_order
from utils.session import (init_session, add_to_cart, remove_from_cart,
                           in_cart, clear_cart, cart_total,
                           require_login, render_sidebar_user)

user = require_login()
render_sidebar_user()
init_session()

PLACEHOLDER = "https://covers.openlibrary.org/b/isbn/0000000000-M.jpg"

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .page-title {
        font-size: 32px; font-weight: 800;
        color: #e94560; margin-bottom: 4px;
    }
    .book-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460; border-radius: 14px;
        padding: 10px 14px 14px 14px; margin-bottom: 4px;
        text-align: center;
    }
    .book-title {
        font-size: 14px; font-weight: 700; color: #e94560;
        min-height: 40px; line-height: 1.4; margin-bottom: 4px;
    }
    .book-author { font-size: 12px; color: #808090; margin: 3px 0; }
    .badge-price {
        background: #0f3460; color: #e94560;
        padding: 3px 10px; border-radius: 20px;
        font-weight: 700; font-size: 12px;
    }
    .badge-rating {
        background: #1a3a1a; color: #4caf50;
        padding: 3px 10px; border-radius: 20px; font-size: 12px;
    }
    .badge-cat {
        background: #2d1a3e; color: #c084fc;
        padding: 3px 10px; border-radius: 20px; font-size: 12px;
    }
    .order-success {
        background: #1a3a1a; border: 1px solid #4caf50;
        border-radius: 10px; padding: 14px;
        color: #4caf50; text-align: center; margin: 8px 0;
    }
    .empty-state { text-align: center; padding: 40px 20px; color: #404060; }
</style>
""", unsafe_allow_html=True)


# ── Buy-Now Handler ───────────────────────────────────────────────────────────
if st.session_state.get("buy_now_product"):
    product = st.session_state.buy_now_product
    with st.spinner(f"Placing order for {product.get('title','')[:30]}..."):
        result = place_order(
            product.get("id"),
            st.session_state.session_id,
            user_id=user["id"]
        )
    if result.get("order_id"):
        st.session_state.last_order_id = result["order_id"]
        st.session_state.order_success = result
    else:
        st.error(f"Order failed: {result.get('error','Unknown error')}")
    st.session_state.buy_now_product = None
    st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Filters + Cart
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔍 Filters")

    categories   = ["All"] + get_categories()
    selected_cat = st.selectbox("Category", categories)

    pr    = get_price_range()
    min_p = int(pr.get("min", 300))
    max_p = int(pr.get("max", 1500))
    price_range = st.slider(
        "Price Range (₹)", min_value=min_p, max_value=max_p,
        value=(min_p, max_p), step=50
    )

    min_rating = st.select_slider(
        "Min Rating",
        options=[4.0, 4.2, 4.4, 4.5, 4.7, 4.8, 4.9],
        value=4.0
    )

    sort_by = st.selectbox(
        "Sort By",
        ["Rating (High→Low)", "Price (Low→High)",
         "Price (High→Low)", "Title (A→Z)"]
    )

    st.divider()

    # ── Cart Panel ────────────────────────────────────────────────────────────
    cart  = st.session_state.get("cart", [])
    total = cart_total()
    st.markdown(f"**🛒 Cart — {len(cart)} item(s)**")

    if not cart:
        st.caption("Your cart is empty.")
    else:
        for p in cart:
            pid = p.get("id")
            c1, c2 = st.columns([3, 1])
            with c1:
                st.caption(f"{p.get('title','')[:24]}...")
                st.caption(f"₹{p.get('price','')}")
            with c2:
                if st.button("🗑", key=f"rm_{pid}"):
                    remove_from_cart(pid)
                    st.rerun()
        st.divider()
        st.markdown(f"**Total: ₹{total:,.0f}**")
        col_clear, col_checkout = st.columns(2)
        with col_clear:
            if st.button("Clear", width='stretch'):
                clear_cart()
                st.rerun()
        with col_checkout:
            if st.button("Checkout", width='stretch', type="primary"):
                st.switch_page("pages/5_Cart.py")

    st.divider()
    if st.button("🤖 Need help choosing?", width='stretch'):
        st.switch_page("pages/2_AIAssistant.py")
    if st.button("📦 My Orders",           width='stretch'):
        st.switch_page("pages/3_Orders.py")
    if st.button("🏠 Home",                width='stretch'):
        st.switch_page("app.py")


# ════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="page-title">🛍️ Browse Books</div>',
            unsafe_allow_html=True)
st.caption("Browse, filter, and buy instantly — no AI needed here.")

# ── Order success banner ──────────────────────────────────────────────────────
if st.session_state.get("order_success"):
    result = st.session_state.order_success
    st.success(
        f"✅ Order placed! Order ID: `{result.get('order_id')}` "
        f"— {result.get('message','')}"
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📦 Track This Order"):
            st.switch_page("pages/3_Orders.py")
    with c2:
        if st.button("Keep Shopping"):
            st.session_state.order_success = None
            st.rerun()
    with c3:
        if st.button("Dismiss"):
            st.session_state.order_success = None
            st.rerun()

# ── Search ────────────────────────────────────────────────────────────────────
search = st.text_input(
    "search", label_visibility="collapsed",
    placeholder="🔎 Search by title, author, or topic..."
)
st.divider()

# ── Fetch + filter ────────────────────────────────────────────────────────────
cat      = None if selected_cat == "All" else selected_cat
products = get_products(category=cat, max_price=price_range[1], limit=100)
products = [p for p in products if p.get("price",  0) >= price_range[0]]
products = [p for p in products if p.get("rating", 0) >= min_rating]

if search.strip():
    q        = search.lower()
    products = [
        p for p in products
        if q in p.get("title",       "").lower()
        or q in p.get("author",      "").lower()
        or q in p.get("category",    "").lower()
        or q in p.get("description", "").lower()
    ]

sort_map = {
    "Rating (High→Low)": lambda p: -p.get("rating", 0),
    "Price (Low→High)":  lambda p:  p.get("price",  0),
    "Price (High→Low)":  lambda p: -p.get("price",  0),
    "Title (A→Z)":       lambda p:  p.get("title",  ""),
}
products = sorted(products, key=sort_map[sort_by])

st.markdown(f"**{len(products)} books found**")

# ── Empty state ───────────────────────────────────────────────────────────────
if not products:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size:48px;">📭</div>
        <div style="font-size:18px; margin:8px 0;">No books found</div>
        <div style="font-size:14px;">Try adjusting your filters.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Book grid (4 columns) ─────────────────────────────────────────────────────
COLS_PER_ROW = 4
for row_start in range(0, len(products), COLS_PER_ROW):
    row_books = products[row_start: row_start + COLS_PER_ROW]
    cols      = st.columns(COLS_PER_ROW)

    for col, book in zip(cols, row_books):
        pid   = book.get("id")
        cover = book.get("cover_url") or PLACEHOLDER

        with col:
            # ✅ st.image() loads external URLs correctly
            try:
                st.image(cover, width='stretch')
            except Exception:
                st.image(PLACEHOLDER, width='stretch')

            # Book info card
            st.markdown(f"""
            <div class="book-card">
                <div class="book-title">{book.get('title','')}</div>
                <div class="book-author">{book.get('author','')}</div>
                <div style="margin-top:8px; display:flex; gap:5px;
                            flex-wrap:wrap; justify-content:center;">
                    <span class="badge-price">₹{book.get('price','')}</span>
                    <span class="badge-rating">⭐ {book.get('rating','')}</span>
                    <span class="badge-cat">{book.get('category','').title()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # View Details
            if st.button("📖 Details", key=f"detail_{pid}",
                         width='stretch'):
                st.session_state.detail_product_id = pid
                st.switch_page("pages/4_Book_Detail.py")

            # Cart + Buy
            b1, b2 = st.columns(2)
            with b1:
                if in_cart(pid):
                    if st.button("✅ Cart", key=f"cart_{pid}",
                                 width='stretch', type="secondary"):
                        remove_from_cart(pid)
                        st.rerun()
                else:
                    if st.button("🛒 Cart", key=f"cart_{pid}",
                                 width='stretch'):
                        add_to_cart(book)
                        st.rerun()
            with b2:
                if st.button("⚡ Buy", key=f"buy_{pid}",
                             width='stretch', type="primary"):
                    st.session_state.buy_now_product = book
                    st.rerun()

            # Ask AI
            with st.expander("🤖 Ask AI"):
                if st.button("Compare & Recommend",
                             key=f"ai_{pid}", width='stretch'):
                    st.session_state.ai_prefill = (
                        f"Tell me about '{book.get('title','')}' "
                        f"and compare with similar "
                        f"{book.get('category','')} books"
                    )
                    st.switch_page("pages/2_AIAssistant.py")

        st.markdown("")