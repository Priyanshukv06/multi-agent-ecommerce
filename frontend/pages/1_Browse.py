import streamlit as st
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.error   import show_api_error, show_connection_banner
from utils.api     import get_products, get_categories, get_price_range, place_order
from utils.session import (
    init_session, add_to_cart, remove_from_cart,
    in_cart, clear_cart, cart_total,
    require_login, render_sidebar_user
)

# ──────────────────────────────────────────────────────────────────────────────
# CACHING FUNCTIONS — Cache API responses for fast filtering
# ──────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_get_categories():
    """Cache category list for 5 minutes."""
    return get_categories()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_get_price_range():
    """Cache price range for 5 minutes."""
    return get_price_range()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def cached_get_products(category=None, max_price=None, limit=100):
    """Cache product list for 5 minutes."""
    return get_products(category=category, max_price=max_price, limit=limit)

st.set_page_config(
    page_title="Browse Books — AI Book Store",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp           { background-color: #0f1117; }
.page-title      { font-size: 32px; font-weight: 800; color: #e94560; margin-bottom: 4px; }
.book-card       { background: linear-gradient(135deg, #1a1a2e, #16213e);
                   border: 1px solid #0f3460; border-radius: 14px;
                   padding: 16px; margin-bottom: 12px; }
.book-title      { font-size: 15px; font-weight: 700; color: #e94560;
                   min-height: 44px; line-height: 1.4; }
.book-author     { font-size: 12px; color: #808090; margin: 4px 0; }
.badge-price     { background: #0f3460; color: #e94560; padding: 3px 10px;
                   border-radius: 20px; font-weight: 700; font-size: 13px; }
.badge-rating    { background: #1a3a1a; color: #4caf50; padding: 3px 10px;
                   border-radius: 20px; font-size: 12px; }
.badge-cat       { background: #2d1a3e; color: #c084fc; padding: 3px 10px;
                   border-radius: 20px; font-size: 12px; }
.empty-state     { text-align: center; padding: 40px 20px; color: #404060; }
.order-success   { background: #1a3a1a; border: 1px solid #4caf50;
                   border-radius: 10px; padding: 14px; color: #4caf50;
                   text-align: center; margin: 8px 0; }
.pagination-bar  { display: flex; justify-content: center; align-items: center;
                   gap: 16px; padding: 16px 0; }
.page-info       { color: #a0a0b0; font-size: 14px; }
</style>
""", unsafe_allow_html=True)

init_session()
user = require_login()           # ← ADDED — auth gate
render_sidebar_user()            # ← ADDED
show_connection_banner()

BOOKS_PER_PAGE = 9

if "browse_page" not in st.session_state:
    st.session_state["browse_page"] = 1


# ── Buy-now handler ───────────────────────────────────────────────────────────
if st.session_state.get("buy_now_product"):
    product    = st.session_state["buy_now_product"]
    product_id = product["id"]
    with st.spinner(f"Placing order for {product['title'][:30]}..."):
        result = place_order(
            product_id,
            st.session_state["session_id"],
            user_id=user.get("id")              # ← FIXED
        )
    if not show_api_error(result, "placing order"):
        if result.get("order_id"):
            st.session_state["last_order_id"] = result["order_id"]
            st.session_state["order_success"]  = result
    st.session_state["buy_now_product"] = None
    st.rerun()


# ── Checkout flow ─────────────────────────────────────────────────────────────
if st.session_state.get("checkout_trigger"):
    st.session_state["checkout_trigger"] = False
    cart = st.session_state.get("cart", [])
    if cart:
        st.markdown("### 🛒 Checkout")
        st.markdown(f"Placing **{len(cart)}** orders...")
        progress = st.progress(0)
        results  = []
        for i, product in enumerate(cart):
            with st.spinner(f"Ordering {product['title'][:30]}..."):
                result = place_order(
                    product["id"],
                    st.session_state["session_id"],
                    user_id=user.get("id")      # ← FIXED
                )
            if not show_api_error(result, f"ordering {product['title'][:20]}"):
                results.append((product, result))
            progress.progress((i + 1) / len(cart))

        if results:
            st.success(f"✅ {len(results)} orders placed successfully!")
            for product, result in results:
                if result.get("order_id"):
                    st.markdown(
                        f'<div class="order-success"><b>{product["title"][:40]}</b>'
                        f'<br>Order ID <code>{result["order_id"]}</code></div>',
                        unsafe_allow_html=True
                    )
                    st.session_state["last_order_id"] = result["order_id"]
        clear_cart()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("📦 Track My Orders", type="primary", use_container_width=True):
                st.switch_page("pages/3_Orders.py")
        with c2:
            if st.button("🛍️ Continue Shopping", use_container_width=True):
                st.rerun()
        st.stop()


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")

    categories   = ["All"] + cached_get_categories()
    selected_cat = st.selectbox("Category", categories)

    pr          = cached_get_price_range()
    min_p       = int(pr.get("min", 300))
    max_p       = int(pr.get("max", 1500))
    price_range = st.slider(
        "Price Range (₹)", min_value=min_p, max_value=max_p,
        value=(min_p, max_p), step=50
    )

    min_rating = st.select_slider(
        "Min Rating", options=[4.0, 4.2, 4.4, 4.5, 4.7, 4.8, 4.9], value=4.0
    )

    sort_by = st.selectbox(
        "Sort By",
        ["Rating High→Low", "Price Low→High", "Price High→Low", "Title A→Z"]
    )

    st.divider()

    cart  = st.session_state.get("cart", [])
    total = cart_total()
    st.markdown(f"### 🛒 Cart ({len(cart)} items)")

    if not cart:
        st.caption("Your cart is empty.")
    else:
        for p in cart:
            pid    = p["id"]
            c1, c2 = st.columns([3, 1])
            with c1:
                st.caption(f"{p['title'][:26]}...")
                st.caption(f"₹{p['price']}")
            with c2:
                if st.button("✕", key=f"rm_{pid}"):
                    remove_from_cart(pid)
                    st.rerun()
        st.divider()
        st.markdown(f"**Total: ₹{total:.0f}**")
        col_clear, col_checkout = st.columns(2)
        with col_clear:
            if st.button("Clear", use_container_width=True):
                clear_cart()
                st.rerun()
        with col_checkout:
            if st.button("Checkout", use_container_width=True, type="primary"):
                st.session_state["checkout_trigger"] = True
                st.rerun()

    st.divider()
    if st.button("🤖 Need help choosing?", use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")    # ← FIXED
    if st.button("📦 My Orders", use_container_width=True):
        st.switch_page("pages/3_Orders.py")


# ── Main Content ──────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">📚 Browse Books</div>', unsafe_allow_html=True)
st.caption("Browse, filter, and buy instantly — no AI needed here.")

search = st.text_input(
    "search", label_visibility="collapsed",
    placeholder="🔍 Search by title, author, or topic..."
)
st.divider()

cat      = None if selected_cat == "All" else selected_cat
products = cached_get_products(category=cat, max_price=price_range[1], limit=100)
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
    "Rating High→Low": lambda p: -p.get("rating", 0),
    "Price Low→High":  lambda p:  p.get("price",  0),
    "Price High→Low":  lambda p: -p.get("price",  0),
    "Title A→Z":       lambda p:  p.get("title",  ""),
}
products = sorted(products, key=sort_map[sort_by])

if not products:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size:48px">📭</div>
        <div style="font-size:18px;margin:8px 0">No books found</div>
        <div style="font-size:14px">Try adjusting your filters or search query</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

total_books  = len(products)
total_pages  = max(1, -(-total_books // BOOKS_PER_PAGE))

page_key = f"{selected_cat}_{price_range}_{min_rating}_{sort_by}_{search}"
if st.session_state.get("_last_filter_key") != page_key:
    st.session_state["browse_page"]      = 1
    st.session_state["_last_filter_key"] = page_key

current_page                    = max(1, min(st.session_state["browse_page"], total_pages))
st.session_state["browse_page"] = current_page

start_idx  = (current_page - 1) * BOOKS_PER_PAGE
end_idx    = start_idx + BOOKS_PER_PAGE
page_books = products[start_idx:end_idx]

st.markdown(
    f"**{total_books}** books found &nbsp;·&nbsp; "
    f"Page **{current_page}** of **{total_pages}**"
)

COLS_PER_ROW = 3
for row_start in range(0, len(page_books), COLS_PER_ROW):
    row_books = page_books[row_start : row_start + COLS_PER_ROW]
    cols      = st.columns(COLS_PER_ROW)

    for col, book in zip(cols, row_books):
        pid = book["id"]
        with col:
            if book.get("cover_url"):
                st.image(book["cover_url"], use_container_width=True)

            st.markdown(f"""
            <div class="book-card">
                <div class="book-title">{book["title"]}</div>
                <div class="book-author">{book["author"]}</div>
                <div style="margin-top:8px;display:flex;gap:6px;flex-wrap:wrap">
                    <span class="badge-price">₹{book["price"]}</span>
                    <span class="badge-rating">⭐ {book["rating"]}</span>
                    <span class="badge-cat">{book.get("category","").title()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            with st.expander("Details"):
                st.caption(book.get("description", ""))
                if st.button("📖 View Full Details", key=f"detail_{pid}",
                             use_container_width=True):
                    st.session_state["detail_product_id"] = pid
                    st.switch_page("pages/4_Book_Detail.py")
                if st.button("🤖 Compare / Recommend", key=f"ai_{pid}",
                             use_container_width=True):
                    st.session_state["ai_prefill"] = (
                        f"Tell me about '{book['title']}' "
                        f"and compare it with similar books"
                    )
                    st.switch_page("pages/2_AI_Assistant.py")   # ← FIXED

            b1, b2 = st.columns(2)
            with b1:
                if in_cart(pid):
                    if st.button("✅ In Cart", key=f"cart_{pid}",
                                 use_container_width=True, type="secondary"):
                        remove_from_cart(pid)
                        st.rerun()
                else:
                    if st.button("🛒 Cart", key=f"cart_{pid}",
                                 use_container_width=True):
                        add_to_cart(book)
                        st.rerun()
            with b2:
                if st.button("⚡ Buy", key=f"buy_{pid}",
                             use_container_width=True, type="primary"):
                    st.session_state["buy_now_product"] = book
                    st.rerun()

st.divider()
prev_col, info_col, next_col = st.columns([1, 3, 1])

with prev_col:
    if st.button("← Prev", use_container_width=True,
                 disabled=(current_page <= 1)):
        st.session_state["browse_page"] -= 1
        st.rerun()

with info_col:
    selected_jump = st.selectbox(
        "Jump to page",
        options=list(range(1, total_pages + 1)),
        index=current_page - 1,
        label_visibility="collapsed",
        key="page_jump"
    )
    if selected_jump != current_page:
        st.session_state["browse_page"] = selected_jump
        st.rerun()
    st.markdown(
        f'<div class="page-info" style="text-align:center">'
        f'Showing {start_idx+1}–{min(end_idx, total_books)} of {total_books} books'
        f'</div>',
        unsafe_allow_html=True
    )

with next_col:
    if st.button("Next →", use_container_width=True,
                 disabled=(current_page >= total_pages)):
        st.session_state["browse_page"] += 1
        st.rerun()