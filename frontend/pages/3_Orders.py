import streamlit as st
import sys
import os
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'frontend'))

from utils.session import require_login, render_sidebar_user, init_session
from utils.api     import initiate_return
from utils.error   import show_api_error, show_connection_banner
from auth.auth     import get_user_orders

st.set_page_config(
    page_title="My Orders — AI Book Store",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0f1117; }
    .page-title {
        font-size: 32px; font-weight: 800; color: #e94560; margin-bottom: 4px;
    }
    .order-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460; border-radius: 14px;
        padding: 18px; margin-bottom: 14px;
    }
    .order-title  { font-size: 17px; font-weight: 700; color: #e94560; }
    .order-meta   { font-size: 13px; color: #a0a0b0; margin: 3px 0; }
    .order-id     { font-family: monospace; color: #c084fc; font-size: 12px; }
    .tl-done      { padding: 6px 0; color: #4caf50; }
    .tl-current   {
        padding: 6px 0 6px 10px; color: #e94560;
        border-left: 3px solid #e94560;
        border-radius: 4px; background: #1a1a2e;
    }
    .tl-pending   { padding: 6px 0; color: #404060; }
    .empty-state  { text-align: center; padding: 60px 20px; color: #404060; }
</style>
""", unsafe_allow_html=True)

init_session()
user = require_login()
render_sidebar_user()
show_connection_banner()

ORDER_FLOW  = ['confirmed', 'packed', 'shipped', 'out_for_delivery', 'delivered']
RETURN_FLOW = ['return_initiated', 'pickup_scheduled', 'picked_up', 'refunded']

STEP_META = {
    'confirmed':        ('✅', 'Order Confirmed'),
    'packed':           ('📦', 'Packed'),
    'shipped':          ('🚚', 'Shipped'),
    'out_for_delivery': ('🏠', 'Out for Delivery'),
    'delivered':        ('🎉', 'Delivered'),
    'cancelled':        ('❌', 'Cancelled'),
    'return_initiated': ('↩️', 'Return Initiated'),
    'pickup_scheduled': ('📅', 'Pickup Scheduled'),
    'picked_up':        ('📬', 'Picked Up'),
    'refunded':         ('💰', 'Refund Processed'),
}

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

ALL_STATUSES   = ['All'] + ORDER_FLOW + ['cancelled'] + RETURN_FLOW
RETURNABLE     = {'delivered'}
NON_RETURNABLE = {'cancelled', 'return_initiated', 'pickup_scheduled', 'picked_up', 'refunded'}


def render_timeline(status: str):
    is_return = status in RETURN_FLOW
    is_cancel = status == 'cancelled'
    flow      = RETURN_FLOW if is_return else ORDER_FLOW

    if is_cancel:
        st.markdown(
            '<div class="tl-current">❌ &nbsp;<b>Cancelled</b></div>',
            unsafe_allow_html=True
        )
        return

    try:
        current_idx = flow.index(status)
    except ValueError:
        current_idx = 0

    for i, step in enumerate(flow):
        icon, label = STEP_META.get(step, ('•', step.replace('_', ' ').title()))
        if i < current_idx:
            st.markdown(
                f'<div class="tl-done">{icon} &nbsp;{label}</div>',
                unsafe_allow_html=True
            )
        elif i == current_idx:
            st.markdown(
                f'<div class="tl-current">{icon} &nbsp;<b>{label}</b>'
                f'&nbsp;<span style="font-size:10px;color:#606070;">● now</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="tl-pending">○ &nbsp;{label}</div>',
                unsafe_allow_html=True
            )


def status_badge(status: str) -> str:
    color = STATUS_COLORS.get(status, '#808090')
    label = STEP_META.get(status, ('', status.replace('_', ' ').title()))[1]
    return (
        f'<span style="background:#1a1a2e; color:{color}; '
        f'border:1px solid {color}; border-radius:12px; '
        f'padding:2px 10px; font-size:12px; font-weight:600;">'
        f'{label}</span>'
    )


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📦 My Orders")
    st.divider()

    filter_status = st.selectbox("Filter by Status", ALL_STATUSES, index=0)

    st.divider()
    if st.button("🛍️ Browse Books", use_container_width=True):
        st.switch_page("pages/1_Browse.py")
    if st.button("🤖 AI Assistant", use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")     # ← FIXED
    if st.button("🛒 Cart",         use_container_width=True):
        st.switch_page("pages/5_Cart.py")
    if st.button("🏠 Home",         use_container_width=True):
        st.switch_page("app.py")


# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-title">📦 My Orders</div>', unsafe_allow_html=True)
st.caption(f"Logged in as **{user['username']}** — showing only your orders")

all_orders = get_user_orders(user["id"])

filtered = all_orders if filter_status == "All" \
           else [o for o in all_orders if o["status"] == filter_status]

st.divider()
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Orders", len(all_orders))
with m2:
    delivered_count = sum(1 for o in all_orders if o["status"] == "delivered")
    st.metric("Delivered", delivered_count)
with m3:
    active_count = sum(
        1 for o in all_orders
        if o["status"] in ('confirmed', 'packed', 'shipped', 'out_for_delivery')
    )
    st.metric("In Transit", active_count)
with m4:
    total_spent = sum(
        o.get("item_price", 0) * o.get("quantity", 1)
        for o in all_orders
        if o["status"] not in ('cancelled', 'refunded')
    )
    st.metric("Total Spent", f"₹{total_spent:,.0f}")
st.divider()

st.caption(f"{len(filtered)} order(s) shown")

if not filtered:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size:52px;">📭</div>
        <div style="font-size:20px; margin:12px 0;">No orders found</div>
        <div style="font-size:14px;">Browse and buy some books to see them here!</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🛍️ Browse Books", type="primary", use_container_width=True):
        st.switch_page("pages/1_Browse.py")
    st.stop()

order_groups: dict = defaultdict(list)
for row in filtered:
    order_groups[row["order_id"]].append(row)

for order_id, items in order_groups.items():
    first   = items[0]
    status  = first["status"]
    created = str(first["created_at"])[:16] if first["created_at"] else "—"   # ← FIXED
    total   = sum(r.get("item_price", 0) * r.get("quantity", 1) for r in items)

    with st.container():
        st.markdown('<div class="order-card">', unsafe_allow_html=True)

        hcol1, hcol2 = st.columns([3, 1])
        with hcol1:
            st.markdown(
                f'<div class="order-id">🆔 {order_id}</div>'
                f'<div class="order-meta">📅 {created} &nbsp;|&nbsp; '
                f'💰 ₹{total:,.0f} &nbsp;|&nbsp; '
                f'{len(items)} item(s)</div>',
                unsafe_allow_html=True
            )
        with hcol2:
            st.markdown(status_badge(status), unsafe_allow_html=True)

        st.markdown("---")

        col_items, col_timeline = st.columns([3, 2])

        with col_items:
            st.markdown("**📚 Items**")
            for item in items:
                st.markdown(
                    f'<div class="order-title">{item["title"][:50]}</div>'
                    f'<div class="order-meta">'
                    f'✍️ {item.get("author","")}&nbsp;|&nbsp;'
                    f'Qty: {item.get("quantity",1)}&nbsp;|&nbsp;'
                    f'₹{item.get("item_price",0):,.0f}'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.markdown("")

        with col_timeline:
            st.markdown("**🗺️ Progress**")
            render_timeline(status)

        st.markdown("")

        act1, act2, act3 = st.columns(3)

        with act1:
            if st.button("🔍 Track", key=f"trk_{order_id}",
                         use_container_width=True):
                st.session_state[f"expand_{order_id}"] = \
                    not st.session_state.get(f"expand_{order_id}", False)
                st.rerun()

        with act2:
            can_return = (status in RETURNABLE)
            if can_return:
                if st.button("↩️ Return", key=f"ret_{order_id}",
                             use_container_width=True):
                    st.session_state[f"return_open_{order_id}"] = True
                    st.rerun()
            elif status in NON_RETURNABLE:
                st.button(
                    "↩️ Returned" if status != 'cancelled' else "❌ Cancelled",
                    key=f"ret_dis_{order_id}",
                    use_container_width=True,
                    disabled=True
                )
            else:
                st.button("↩️ Return (not yet)",
                          key=f"ret_na_{order_id}",
                          use_container_width=True,
                          disabled=True)

        with act3:
            if st.button("🤖 Ask AI", key=f"ai_{order_id}",
                         use_container_width=True):
                st.session_state["ai_prefill"] = \
                    f"Tell me about my order {order_id}"
                st.switch_page("pages/2_AI_Assistant.py")    # ← FIXED

        if st.session_state.get(f"return_open_{order_id}"):
            with st.form(key=f"return_form_{order_id}"):
                st.markdown("**↩️ Initiate Return**")
                reason = st.text_area(
                    "Reason for return",
                    placeholder="e.g. Wrong book delivered, damaged, etc.",
                    max_chars=200
                )
                rc1, rc2 = st.columns(2)
                with rc1:
                    submitted = st.form_submit_button(
                        "Submit Return", type="primary",
                        use_container_width=True
                    )
                with rc2:
                    cancelled_form = st.form_submit_button(
                        "Cancel", use_container_width=True
                    )

                if submitted:
                    if not reason.strip():
                        st.error("Please enter a reason.")
                    else:
                        result = initiate_return(
                            order_id, reason,
                            st.session_state.get("session_id", "default"),
                            user_id=user["id"]
                        )
                        if not show_api_error(result, "initiating return"):
                            if result.get("return_id") or result.get("status"):
                                st.success("✅ Return initiated successfully!")
                                st.session_state[f"return_open_{order_id}"] = False
                                st.rerun()
                            else:
                                st.error(f"Failed: {result.get('error', 'Unknown error')}")

                if cancelled_form:
                    st.session_state[f"return_open_{order_id}"] = False
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("")