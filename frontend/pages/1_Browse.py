import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.api     import get_products, get_categories, get_price_range, place_order, place_bulk_orders
from utils.session import init_session, add_to_cart, remove_from_cart, in_cart, clear_cart, cart_total

st.set_page_config(
    page_title="Browse Books — AI Book Store",
    page_icon="🛍️",
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
    .book-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        height: 100%;
    }
    .book-title {
        font-size: 15px; font-weight: 700;
        color: #e94560; min-height: 44px;
        line-height: 1.4;
    }
    .book-author { font-size: 12px; color: #808090; margin: 4px 0; }
    .badge-price {
        background: #0f3460; color: #e94560;
        padding: 3px 10px; border-radius: 20px;
        font-weight: 700; font-size: 13px;
    }
    .badge-rating {
        background: #1a3a1a; color: #4caf50;
        padding: 3px 10px; border-radius: 20px;
        font-size: 12px;
    }
    .badge-cat {
        background: #2d1a3e; color: #c084fc;
        padding: 3px 10px; border-radius: 20px;
        font-size: 12px;
    }
    .cart-panel {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 12px; padding: 16px;
    }
    .empty-state {
        text-align: center; padding: 40px 20px;
        color: #404060;
    }
    .order-success {
        background: #1a3a1a; border: 1px solid #4caf50;
        border-radius: 10px; padding: 14px;
        color: #4caf50; text-align: center;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

init_session()

# ── Buy-now handler ───────────────────────────────────────────────────────────
if "buy_now_product" in st.session_state and st.session_state.buy_now_product:
    product = st.session_state.buy_now_product
    with st.spinner(f"Placing order for {product['title'][:30]}..."):
        result = place_order(product["id"], st.session_state.session_id)
    if result.get("order_id"):
        st.session_state.last_order_id = result["order_id"]
        st.session_state.order_success = result
    st.session_state.buy_now_product = None
    st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR — Filters + Cart
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🔎 Filters")

    # Category filter
    categories  = ["All"] + get_categories()
    selected_cat = st.selectbox("Category", categories)

    # Price filter
    pr        = get_price_range()
    min_p     = int(pr.get("min", 300))
    max_p     = int(pr.get("max", 1500))
    price_range = st.slider(
        "Price Range (₹)",
        min_value=min_p, max_value=max_p,
        value=(min_p, max_p), step=50
    )

    # Rating filter
    min_rating = st.select_slider(
        "Min Rating",
        options=[4.0, 4.2, 4.4, 4.5, 4.7, 4.8, 4.9],
        value=4.0
    )

    # Sort
    sort_by = st.selectbox(
        "Sort By",
        ["Rating (High → Low)", "Price (Low → High)",
         "Price (High → Low)", "Title (A → Z)"]
    )

    st.divider()

    # ── Cart Panel ────────────────────────────────────────────────────────────
    cart  = st.session_state.get("cart", [])
    total = cart_total()

    st.markdown(f"### 🛒 Cart ({len(cart)} items)")

    if not cart:
        st.caption("Your cart is empty.\nBrowse books and add to cart!")
    else:
        for p in cart:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.caption(f"📗 {p['title'][:28]}...")
                st.caption(f"₹{p['price']}")
            with c2:
                if st.button("✕", key=f"rm_{p['id']}"):
                    remove_from_cart(p["id"])
                    st.rerun()

        st.divider()
        st.markdown(f"**Total: ₹{total:.0f}**")

        col_clear, col_checkout = st.columns(2)
        with col_clear:
            if st.button("🗑 Clear", use_container_width=True):
                clear_cart()
                st.rerun()
        with col_checkout:
            if st.button("✅ Checkout", use_container_width=True, type="primary"):
                st.session_state.checkout_trigger = True
                st.rerun()

    st.divider()
    if st.button("🤖 Need help choosing?", use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")
    if st.button("📦 My Orders", use_container_width=True):
        st.switch_page("pages/3_Orders.py")


# ════════════════════════════════════════════════════════════════════════════
# CHECKOUT FLOW
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.get("checkout_trigger"):
    st.session_state.checkout_trigger = False
    cart = st.session_state.get("cart", [])

    if cart:
        st.markdown("## 🧾 Checkout")
        st.markdown(f"Placing **{len(cart)} order(s)**...")

        progress = st.progress(0)
        results  = []

        for i, product in enumerate(cart):
            with st.spinner(f"Ordering '{product['title'][:30]}'..."):
                result = place_order(product["id"], st.session_state.session_id)
                results.append((product, result))
            progress.progress((i + 1) / len(cart))

        st.success(f"✅ {len(results)} order(s) placed successfully!")

        for product, result in results:
            if result.get("order_id"):
                st.markdown(f"""
                <div class="order-success">
                    📦 <b>{product['title'][:40]}</b><br>
                    Order ID: <code>{result['order_id']}</code>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.last_order_id = result["order_id"]

        clear_cart()

        if st.button("📦 Track My Orders", type="primary"):
            st.switch_page("pages/3_Orders.py")
        st.stop()


# ════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="page-title">🛍️ Browse Books</div>', unsafe_allow_html=True)
st.caption("No AI needed here — just browse, filter, and buy instantly.")

# ── Order success banner ───────────────────────────────────────────────────
if st.session_state.get("order_success"):
    result = st.session_state.order_success
    st.success(
        f"✅ Order placed! **Order ID:** `{result.get('order_id')}` — "
        f"{result.get('message', '')}"
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 Track This Order"):
            st.switch_page("pages/3_Orders.py")
    with col2:
        if st.button("✕ Dismiss"):
            st.session_state.order_success = None
            st.rerun()

# ── Search bar ─────────────────────────────────────────────────────────────
search = st.text_input(
    "🔍 Search books...",
    placeholder="e.g. Python, Neural Networks, Scikit-Learn",
    label_visibility="collapsed"
)

st.divider()

# ── Fetch + filter products ────────────────────────────────────────────────
cat      = None if selected_cat == "All" else selected_cat
products = get_products(category=cat, max_price=price_range[1], limit=50)

# Apply min price filter
products = [p for p in products if p.get("price", 0) >= price_range[0]]

# Apply min rating filter
products = [p for p in products if p.get("rating", 0) >= min_rating]

# Apply search filter
if search.strip():
    q = search.lower()
    products = [
        p for p in products
        if q in p.get("title",  "").lower()
        or q in p.get("author", "").lower()
        or q in p.get("category", "").lower()
        or q in p.get("description", "").lower()
    ]

# Apply sort
sort_map = {
    "Rating (High → Low)":  lambda p: -p.get("rating", 0),
    "Price (Low → High)":   lambda p:  p.get("price",  0),
    "Price (High → Low)":   lambda p: -p.get("price",  0),
    "Title (A → Z)":        lambda p:  p.get("title",  ""),
}
products = sorted(products, key=sort_map[sort_by])

# ── Results count ──────────────────────────────────────────────────────────
cart_ids = {p["id"] for p in st.session_state.get("cart", [])}
st.markdown(f"**{len(products)} books found**")

if not products:
    st.markdown("""
    <div class="empty-state">
        <div style='font-size:48px;'>📭</div>
        <div style='font-size:18px; margin:8px 0;'>No books found</div>
        <div style='font-size:14px;'>Try adjusting your filters or search query</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── Book Grid (3 columns) ──────────────────────────────────────────────────
cols_per_row = 3
for row_start in range(0, len(products), cols_per_row):
    row_products = products[row_start : row_start + cols_per_row]
    cols         = st.columns(cols_per_row)

    for col, book in zip(cols, row_products):
        pid = book["id"]
        with col:
            # Card HTML
            st.markdown(f"""
            <div class="book-card">
                <div class="book-title">{book["title"]}</div>
                <div class="book-author">✍️ {book["author"]}</div>
                <div style='margin-top:8px; display:flex; gap:6px; flex-wrap:wrap;'>
                    <span class="badge-price">₹{book["price"]}</span>
                    <span class="badge-rating">⭐ {book["rating"]}/5</span>
                    <span class="badge-cat">📂 {book["category"].title()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Description expander
            with st.expander("📄 Details"):
                st.caption(book.get("description", ""))
                st.markdown("**Ask AI about this book:**")
                if st.button("🤖 Compare / Recommend", key=f"ai_{pid}",
                             use_container_width=True):
                    st.session_state.ai_prefill = (
                        f"Tell me about '{book['title']}' "
                        f"and compare it with similar books"
                    )
                    st.switch_page("pages/2_AI_Assistant.py")

            # Buy + Cart buttons
            b1, b2 = st.columns(2)
            with b1:
                already_in_cart = in_cart(pid)
                if already_in_cart:
                    if st.button("🛒 In Cart", key=f"cart_{pid}",
                                 use_container_width=True, type="secondary"):
                        remove_from_cart(pid)
                        st.rerun()
                else:
                    if st.button("➕ Cart", key=f"cart_{pid}",
                                 use_container_width=True):
                        add_to_cart(book)
                        st.rerun()
            with b2:
                if st.button("⚡ Buy Now", key=f"buy_{pid}",
                             use_container_width=True, type="primary"):
                    st.session_state.buy_now_product = book
                    st.rerun()