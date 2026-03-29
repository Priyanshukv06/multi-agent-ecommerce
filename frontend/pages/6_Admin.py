import streamlit as st
import sys
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'frontend'))

st.set_page_config(
    page_title="Admin Dashboard — AI Book Store",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

from utils.session import require_admin, render_sidebar_user
from auth.auth     import (
    get_all_users,
    get_all_orders_admin,
    update_order_status,
    clear_all_orders,
    get_stock,
    update_stock,
)

import sqlite3

user = require_admin()          # blocks non-admins automatically
render_sidebar_user()


# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .page-title {
        font-size: 32px; font-weight: 800; color: #e94560; margin-bottom: 4px;
    }
    .stat-box {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 12px; padding: 20px; text-align: center;
    }
    .stat-num   { font-size: 36px; font-weight: 800; color: #e94560; }
    .stat-label { font-size: 13px; color: #808090; margin-top: 4px; }
    .section-title {
        font-size: 20px; font-weight: 700;
        color: #e0e0e0; margin: 20px 0 10px 0;
    }
    .order-row {
        background: #1a1a2e; border: 1px solid #0f3460;
        border-radius: 10px; padding: 14px; margin-bottom: 10px;
    }
    .user-row {
        background: #16213e; border: 1px solid #0f3460;
        border-radius: 10px; padding: 12px; margin-bottom: 8px;
    }
    .badge-admin { background: #3a1a00; color: #f97316;
                   padding: 2px 10px; border-radius: 12px; font-size: 12px; }
    .badge-user  { background: #1a2a3a; color: #60a5fa;
                   padding: 2px 10px; border-radius: 12px; font-size: 12px; }
    .danger-box {
        background: #2a0a0a; border: 1px solid #ef4444;
        border-radius: 12px; padding: 20px; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)


# ── Constants ─────────────────────────────────────────────────────────────────
ORDER_STATUSES = [
    'confirmed', 'packed', 'shipped',
    'out_for_delivery', 'delivered',
    'cancelled',
    'return_initiated', 'pickup_scheduled', 'picked_up', 'refunded'
]

STATUS_COLORS = {
    'confirmed':        '#f59e0b',
    'packed':           '#60a5fa',
    'shipped':          '#a78bfa',
    'out_for_delivery': '#fb923c',
    'delivered':        '#4ade80',
    'cancelled':        '#f87171',
    'return_initiated': '#fbbf24',
    'pickup_scheduled': '#34d399',
    'picked_up':        '#67e8f9',
    'refunded':         '#4ade80',
}


def status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, '#808090')
    label = status.replace('_', ' ').title()
    return (
        f'<span style="background:#1a1a2e; color:{color}; '
        f'border: 1px solid {color}; border-radius:12px; '
        f'padding:2px 10px; font-size:12px; font-weight:600;">'
        f'{label}</span>'
    )


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 👑 Admin Panel")
    st.divider()
    if st.button("🛍️ Browse Books",  use_container_width=True):
        st.switch_page("pages/1_Browse.py")
    if st.button("📦 All Orders",    use_container_width=True):
        st.switch_page("pages/3_Orders.py")
    if st.button("🏠 Home",          use_container_width=True):
        st.switch_page("app.py")


# ════════════════════════════════════════════════════════════════════════════
# HEADER
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="page-title">👑 Admin Dashboard</div>',
            unsafe_allow_html=True)
st.caption(f"Logged in as **{user['username']}** (Admin)")
st.divider()


# ── Load data ─────────────────────────────────────────────────────────────────
all_orders = get_all_orders_admin()
all_users  = get_all_users()

# Unique orders (multiple rows per order due to items join)
unique_order_ids = list(dict.fromkeys(o["order_id"] for o in all_orders))


# ════════════════════════════════════════════════════════════════════════════
# STATS ROW
# ════════════════════════════════════════════════════════════════════════════
total_orders    = len(unique_order_ids)
total_users     = len([u for u in all_users if u["role"] == "user"])
delivered_count = len(set(
    o["order_id"] for o in all_orders if o["status"] == "delivered"
))
revenue         = sum(
    o.get("item_price", 0) * o.get("quantity", 1)
    for o in all_orders
    if o["status"] not in ("cancelled", "refunded")
)

c1, c2, c3, c4 = st.columns(4)
stats = [
    (str(total_orders),    "Total Orders"),
    (str(total_users),     "Registered Users"),
    (str(delivered_count), "Delivered"),
    (f"₹{revenue:,.0f}",  "Total Revenue"),
]
for col, (num, label) in zip([c1, c2, c3, c4], stats):
    with col:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-num">{num}</div>
            <div class="stat-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tab_orders, tab_users, tab_stock, tab_danger = st.tabs([
    f"📦 Orders ({total_orders})",
    f"👥 Users ({total_users})",
    "📚 Stock Manager",
    "⚠️ Danger Zone",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — ORDER MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════
with tab_orders:
    st.markdown('<div class="section-title">📦 All Orders — Simulate Status</div>',
                unsafe_allow_html=True)

    # Filter controls
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        filter_user = st.selectbox(
            "Filter by User",
            ["All Users"] + list(set(o.get("username", "") for o in all_orders))
        )
    with fc2:
        filter_status = st.selectbox(
            "Filter by Status",
            ["All Statuses"] + ORDER_STATUSES
        )
    with fc3:
        search_order = st.text_input(
            "search_order", label_visibility="collapsed",
            placeholder="🔎 Search Order ID or book title..."
        )

    st.divider()

    # Group rows by order_id
    from collections import defaultdict
    order_groups: dict = defaultdict(list)
    for row in all_orders:
        order_groups[row["order_id"]].append(row)

    # Apply filters
    filtered_orders = {}
    for oid, items in order_groups.items():
        first = items[0]
        if filter_user   != "All Users"    and first.get("username") != filter_user:
            continue
        if filter_status != "All Statuses" and first.get("status")   != filter_status:
            continue
        if search_order.strip():
            q = search_order.lower()
            match = (
                q in oid.lower() or
                any(q in i.get("title", "").lower() for i in items)
            )
            if not match:
                continue
        filtered_orders[oid] = items

    st.caption(f"{len(filtered_orders)} order(s) shown")

    if not filtered_orders:
        st.info("No orders match the current filter.")
    else:
        for order_id, items in filtered_orders.items():
            first   = items[0]
            status  = first.get("status", "confirmed")
            uname   = first.get("username", "unknown")
            created = first.get("created_at", "")[:16]
            total   = sum(
                r.get("item_price", 0) * r.get("quantity", 1) for r in items
            )

            with st.container():
                st.markdown('<div class="order-row">', unsafe_allow_html=True)

                row1, row2 = st.columns([3, 2])
                with row1:
                    st.markdown(
                        f'<span style="font-family:monospace; color:#c084fc;">'
                        f'{order_id}</span>'
                        f'&nbsp;&nbsp;{status_badge(status)}',
                        unsafe_allow_html=True
                    )
                    st.caption(
                        f"👤 {uname}  |  📅 {created}  |  "
                        f"💰 ₹{total:,.0f}  |  {len(items)} item(s)"
                    )
                    for item in items:
                        st.markdown(
                            f'<span style="color:#a0a0b0; font-size:13px;">'
                            f'📚 {item.get("title","")[:45]} '
                            f'x{item.get("quantity",1)}'
                            f'</span>',
                            unsafe_allow_html=True
                        )

                with row2:
                    st.markdown("**🔄 Simulate Status**")
                    new_status = st.selectbox(
                        "new_status", ORDER_STATUSES,
                        index=ORDER_STATUSES.index(status) if status in ORDER_STATUSES else 0,
                        key=f"sel_{order_id}",
                        label_visibility="collapsed"
                    )
                    if st.button("✅ Update Status",
                                 key=f"upd_{order_id}",
                                 use_container_width=True,
                                 type="primary"):
                        if update_order_status(order_id, new_status):
                            st.success(f"✅ Updated to **{new_status}**")
                            st.rerun()
                        else:
                            st.error("Update failed.")

                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — USER MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════
with tab_users:
    st.markdown('<div class="section-title">👥 Registered Users</div>',
                unsafe_allow_html=True)

    # Per-user order counts
    user_order_counts = defaultdict(int)
    for oid, items in order_groups.items():
        uname = items[0].get("username", "")
        user_order_counts[uname] += 1

    for u in all_users:
        role_badge = (
            '<span class="badge-admin">👑 Admin</span>'
            if u["role"] == "admin"
            else '<span class="badge-user">👤 User</span>'
        )
        order_count = user_order_counts.get(u["username"], 0)
        joined      = u.get("created_at", "")[:10]

        st.markdown('<div class="user-row">', unsafe_allow_html=True)
        uc1, uc2, uc3 = st.columns([2, 2, 2])

        with uc1:
            st.markdown(
                f'<b style="color:#e0e0e0; font-size:15px;">{u["username"]}</b>'
                f'&nbsp;&nbsp;{role_badge}',
                unsafe_allow_html=True
            )
            st.caption(f"🆔 ID: {u['id']}  |  📅 Joined: {joined}")

        with uc2:
            st.metric("Total Orders", order_count)

        with uc3:
            if st.button(
                f"📦 View Orders",
                key=f"view_orders_{u['id']}",
                use_container_width=True
            ):
                st.session_state["admin_filter_user"] = u["username"]
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # Show filtered orders if admin clicked "View Orders"
    if st.session_state.get("admin_filter_user"):
        target = st.session_state.admin_filter_user
        st.markdown(f"---")
        st.markdown(f"**📦 Orders for `{target}`**")

        user_orders = {
            oid: items for oid, items in order_groups.items()
            if items[0].get("username") == target
        }

        if not user_orders:
            st.info(f"No orders found for {target}.")
        else:
            for oid, items in user_orders.items():
                first  = items[0]
                status = first.get("status", "confirmed")
                total  = sum(
                    r.get("item_price", 0) * r.get("quantity", 1) for r in items
                )
                st.markdown(
                    f'`{oid}` &nbsp; {status_badge(status)} &nbsp; '
                    f'₹{total:,.0f}',
                    unsafe_allow_html=True
                )
                for item in items:
                    st.caption(
                        f"   📚 {item.get('title','')[:50]}  "
                        f"x{item.get('quantity',1)}"
                    )
                st.markdown("")

        if st.button("✖ Close", use_container_width=False):
            st.session_state.admin_filter_user = None
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — STOCK MANAGER
# ════════════════════════════════════════════════════════════════════════════
with tab_stock:
    st.markdown('<div class="section-title">📚 Stock Manager</div>',
                unsafe_allow_html=True)

    DB_PATH = os.path.join(ROOT, "data", "products.db")

    @st.cache_data(ttl=10)
    def load_products_with_stock():
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT p.id, p.title, p.author, p.category, p.price,
                   COALESCE(s.quantity, 0) AS stock
            FROM products p
            LEFT JOIN stock s ON p.id = s.product_id
            ORDER BY p.category, p.title
        """).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    products_stock = load_products_with_stock()

    # Filter
    sc1, sc2 = st.columns([2, 1])
    with sc1:
        stock_search = st.text_input(
            "stock_search", label_visibility="collapsed",
            placeholder="🔎 Search by title or category..."
        )
    with sc2:
        show_low = st.checkbox("⚠️ Show low stock only (≤ 10)", value=False)

    filtered_products = products_stock
    if stock_search.strip():
        q                = stock_search.lower()
        filtered_products = [
            p for p in filtered_products
            if q in p.get("title", "").lower()
            or q in p.get("category", "").lower()
        ]
    if show_low:
        filtered_products = [
            p for p in filtered_products if p.get("stock", 0) <= 10
        ]

    st.caption(f"{len(filtered_products)} book(s) shown")
    st.divider()

    # Low stock alert
    low_stock = [p for p in products_stock if p.get("stock", 0) <= 5]
    if low_stock:
        st.warning(
            f"⚠️ **{len(low_stock)} books** have stock ≤ 5: "
            + ", ".join(p["title"][:25] for p in low_stock[:4])
            + ("..." if len(low_stock) > 4 else "")
        )

    # Stock grid (4 per row)
    COLS = 4
    for row_start in range(0, len(filtered_products), COLS):
        row_p = filtered_products[row_start: row_start + COLS]
        cols  = st.columns(COLS)
        for col, p in zip(cols, row_p):
            pid   = p["id"]
            stock = p.get("stock", 0)
            with col:
                # Stock color
                if stock == 0:
                    color = "#ef4444"
                    icon  = "❌"
                elif stock <= 5:
                    color = "#f59e0b"
                    icon  = "⚠️"
                elif stock <= 10:
                    color = "#fbbf24"
                    icon  = "🟡"
                else:
                    color = "#4caf50"
                    icon  = "✅"

                st.markdown(f"""
                <div style="background:#1a1a2e; border:1px solid #0f3460;
                            border-radius:10px; padding:12px; margin-bottom:4px;">
                    <div style="font-size:13px; font-weight:700;
                                color:#e94560; min-height:36px;">
                        {p['title'][:38]}
                    </div>
                    <div style="font-size:11px; color:#808090; margin:3px 0;">
                        📂 {p.get('category','').title()}
                    </div>
                    <div style="font-size:18px; font-weight:800;
                                color:{color}; margin:6px 0;">
                        {icon} {stock} left
                    </div>
                </div>
                """, unsafe_allow_html=True)

                new_qty = st.number_input(
                    "New stock",
                    min_value=0, max_value=999,
                    value=stock, step=1,
                    key=f"stock_{pid}",
                    label_visibility="collapsed"
                )
                if st.button("💾 Save", key=f"save_stock_{pid}",
                             use_container_width=True):
                    update_stock(pid, new_qty)
                    st.cache_data.clear()
                    st.success(f"✅ Updated to {new_qty}")
                    st.rerun()


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — DANGER ZONE
# ════════════════════════════════════════════════════════════════════════════
with tab_danger:
    st.markdown('<div class="section-title">⚠️ Danger Zone</div>',
                unsafe_allow_html=True)
    st.error("These actions are **irreversible**. Use with caution.")

    st.markdown('<div class="danger-box">', unsafe_allow_html=True)

    # ── Clear all orders ──────────────────────────────────────────────────────
    st.markdown("#### 🗑️ Clear All Orders")
    st.caption(
        "Deletes all orders, order items and returns. "
        "Books and users are kept. Good for demo reset."
    )
    if st.button("🗑️ Clear All Orders", type="primary", use_container_width=False):
        st.session_state["confirm_clear_orders"] = True

    if st.session_state.get("confirm_clear_orders"):
        st.warning("⚠️ Are you sure? This cannot be undone.")
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("✅ Yes, delete all orders",
                         use_container_width=True, type="primary"):
                count = clear_all_orders()
                st.success(f"✅ Deleted {count} orders.")
                st.session_state["confirm_clear_orders"] = False
                st.rerun()
        with cc2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state["confirm_clear_orders"] = False
                st.rerun()

    st.markdown("---")

    # ── Full DB reset ─────────────────────────────────────────────────────────
    st.markdown("#### 💣 Full Database Reset")
    st.caption(
        "Drops and recreates ALL tables. Re-seeds 103 books + default users. "
        "**All orders, returns and chat history will be lost.**"
    )
    if st.button("💣 Full Reset (Nuclear)", use_container_width=False):
        st.session_state["confirm_full_reset"] = True

    if st.session_state.get("confirm_full_reset"):
        st.error("⛔ This will wipe EVERYTHING. Type **RESET** to confirm.")
        confirm_text = st.text_input("Type RESET to confirm:",
                                      key="reset_confirm_text")
        rc1, rc2 = st.columns(2)
        with rc1:
            if st.button("💣 Confirm Full Reset",
                         use_container_width=True, type="primary"):
                if confirm_text.strip() == "RESET":
                    with st.spinner("Resetting database..."):
                        try:
                            result = os.popen(
                                f"python {ROOT}/data/seed_products.py"
                            ).read()
                            st.success("✅ Database reset complete! 103 books re-seeded.")
                            st.code(result)
                            st.session_state["confirm_full_reset"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {str(e)}")
                else:
                    st.error("❌ You must type exactly RESET to confirm.")
        with rc2:
            if st.button("❌ Cancel Reset", use_container_width=True):
                st.session_state["confirm_full_reset"] = False
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)