import streamlit as st
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.api     import track_order, initiate_return, get_history
from utils.session import init_session

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
        font-size: 32px; font-weight: 800;
        color: #e94560; margin-bottom: 4px;
    }
    .order-card {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 1px solid #0f3460;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .order-id {
        font-family: monospace; font-size: 13px;
        color: #c084fc; background: #2d1a3e;
        padding: 2px 8px; border-radius: 6px;
    }
    .order-title {
        font-size: 18px; font-weight: 700;
        color: #e0e0e0; margin: 8px 0 4px;
    }
    .status-confirmed    { color: #60a5fa; }
    .status-shipped      { color: #f59e0b; }
    .status-delivered    { color: #4caf50; }
    .status-cancelled    { color: #ef4444; }
    .status-return       { color: #f97316; }
    .timeline-done  {
        padding: 6px 0 6px 12px;
        border-left: 2px solid #4caf50;
        color: #4caf50; font-size: 14px;
    }
    .timeline-current {
        padding: 6px 0 6px 12px;
        border-left: 2px solid #e94560;
        color: #e94560; font-size: 14px;
        font-weight: 700;
    }
    .timeline-pending {
        padding: 6px 0 6px 12px;
        border-left: 2px solid #2d2d4e;
        color: #404060; font-size: 14px;
    }
    .empty-state {
        text-align: center; padding: 60px 20px; color: #404060;
    }
    .return-box {
        background: #1a1208; border: 1px solid #f97316;
        border-radius: 10px; padding: 14px; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

init_session()

# ── State Machine Config ──────────────────────────────────────────────────────
ACTIVE_STATES = [
    ("confirmed",        "📦", "Order Confirmed",     "Confirmed and being packed"),
    ("packed",           "📫", "Packed",              "Packed and ready to ship"),
    ("shipped",          "🚚", "Shipped",             "In transit to your location"),
    ("out_for_delivery", "🏍️",  "Out for Delivery",   "With delivery partner today"),
    ("delivered",        "✅", "Delivered",           "Successfully delivered"),
]

RETURN_STATES = [
    ("return_initiated", "🔄", "Return Initiated",    "Awaiting pickup scheduling"),
    ("pickup_scheduled", "📅", "Pickup Scheduled",    "Pickup scheduled within 2 days"),
    ("picked_up",        "📤", "Picked Up",           "Item picked up, processing refund"),
    ("refunded",         "💰", "Refund Processed",    "Refund credited in 3-5 business days"),
]

STATUS_COLORS = {
    "confirmed":        "#60a5fa",
    "packed":           "#60a5fa",
    "shipped":          "#f59e0b",
    "out_for_delivery": "#f59e0b",
    "delivered":        "#4caf50",
    "cancelled":        "#ef4444",
    "return_initiated": "#f97316",
    "pickup_scheduled": "#f97316",
    "picked_up":        "#f97316",
    "refunded":         "#4caf50",
}

STATE_MESSAGES = {
    "confirmed":        "Your order is confirmed and being packed.",
    "packed":           "Your order has been packed and is ready to ship.",
    "shipped":          "Your order is on its way!",
    "out_for_delivery": "Your order will be delivered today.",
    "delivered":        "Your order has been delivered. Enjoy your book! 🎉",
    "cancelled":        "This order has been cancelled.",
    "return_initiated": "Return initiated. Pickup within 2 business days.",
    "pickup_scheduled": "Pickup has been scheduled.",
    "picked_up":        "Your item has been picked up. Refund in progress.",
    "refunded":         "Refund processed. Credit in 3-5 business days.",
}


def get_state_list(status: str):
    return_statuses = {s[0] for s in RETURN_STATES}
    return RETURN_STATES if status in return_statuses else ACTIVE_STATES


def render_timeline(status: str):
    """Pure state machine timeline — zero AI calls."""
    states     = get_state_list(status)
    status_ids = [s[0] for s in states]

    try:
        current_idx = status_ids.index(status)
    except ValueError:
        current_idx = 0

    for i, (state_id, icon, label, desc) in enumerate(states):
        if i < current_idx:
            st.markdown(
                f'<div class="timeline-done">✅ {label}</div>',
                unsafe_allow_html=True
            )
        elif i == current_idx:
            st.markdown(
                f'<div class="timeline-current">'
                f'{icon} {label} &nbsp;<span style="font-size:11px; '
                f'background:#e94560; color:white; padding:2px 6px; '
                f'border-radius:10px;">CURRENT</span>'
                f'<br><span style="font-weight:400; font-size:12px; '
                f'color:#a0a0b0;">{desc}</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="timeline-pending">⬜ {label}</div>',
                unsafe_allow_html=True
            )


def render_order_card(order: dict, idx: int):
    """Render full order card with timeline + return option."""
    status    = order.get("status", "confirmed")
    color     = STATUS_COLORS.get(status, "#60a5fa")
    order_id  = order.get("order_id", "")
    is_return = status in {s[0] for s in RETURN_STATES}

    with st.container():
        st.markdown(f"""
        <div class="order-card">
            <div style="display:flex; justify-content:space-between;
                        align-items:center; flex-wrap:wrap; gap:8px;">
                <span class="order-id">{order_id}</span>
                <span style="background:{color}22; color:{color};
                             padding:4px 12px; border-radius:20px;
                             font-size:13px; font-weight:700;">
                    ● {status.replace("_", " ").title()}
                </span>
            </div>
            <div class="order-title">{order.get("title", "")[:55]}</div>
            <div style="color:#808090; font-size:13px;">
                ✍️ {order.get("author","")} &nbsp;|&nbsp;
                💰 ₹{order.get("price","")} &nbsp;|&nbsp;
                📅 Ordered: {order.get("created_at","")[:10]}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Status message
        msg = STATE_MESSAGES.get(status, "Processing your order.")
        if status == "delivered":
            st.success(f"✅ {msg}")
        elif status == "cancelled":
            st.error(f"❌ {msg}")
        elif is_return:
            st.warning(f"🔄 {msg}")
        else:
            st.info(f"ℹ️ {msg}")

        # Timeline + actions in two columns
        col_timeline, col_actions = st.columns([3, 2])

        with col_timeline:
            st.markdown("**📍 Order Progress**")
            render_timeline(status)
            if status not in ("delivered", "cancelled", "refunded"):
                st.caption(f"🏁 Estimated Delivery: **{order.get('eta', 'N/A')}**")

        with col_actions:
            st.markdown("**⚡ Actions**")

            # Track / Refresh
            if st.button("🔄 Refresh Status", key=f"refresh_{idx}",
                         use_container_width=True):
                st.cache_data.clear()
                st.rerun()

            # Return button — only for eligible orders
            returnable = status in ("confirmed", "packed", "shipped",
                                    "out_for_delivery", "delivered")
            if returnable:
                with st.expander("↩️ Return this order"):
                    st.markdown('<div class="return-box">', unsafe_allow_html=True)
                    reason_options = [
                        "Select a reason...",
                        "Wrong item received",
                        "Damaged or defective",
                        "No longer needed",
                        "Better price available",
                        "Other",
                    ]
                    reason = st.selectbox(
                        "Return reason",
                        reason_options,
                        key=f"reason_{idx}",
                        label_visibility="collapsed"
                    )
                    if reason != "Select a reason...":
                        if st.button("✅ Confirm Return",
                                     key=f"confirm_return_{idx}",
                                     use_container_width=True,
                                     type="primary"):
                            with st.spinner("Initiating return..."):
                                result = initiate_return(
                                    order_id,
                                    reason,
                                    st.session_state.session_id
                                )
                            if result.get("return_id"):
                                st.success(
                                    f"✅ Return initiated!\n\n"
                                    f"**Return ID:** `{result['return_id']}`\n\n"
                                    f"{result.get('message','')}"
                                )
                                st.rerun()
                            elif result.get("detail"):
                                st.error(f"❌ {result['detail']}")
                    st.markdown('</div>', unsafe_allow_html=True)

            # Already in return
            if is_return:
                st.info("↩️ Return in progress")

            # Delivered — ask AI for next book
            if status == "delivered":
                if st.button("🤖 Recommend next book",
                             key=f"ai_next_{idx}",
                             use_container_width=True):
                    st.session_state.ai_prefill = (
                        f"I just finished reading '{order.get('title','')}'. "
                        f"What should I read next?"
                    )
                    st.switch_page("pages/2_AI_Assistant.py")

        st.divider()


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 📦 Orders")

    # Manual order lookup
    st.markdown("**🔍 Track by Order ID**")
    manual_id = st.text_input("Order ID", placeholder="ORD-00001",
                              label_visibility="collapsed")
    if st.button("Track", use_container_width=True) and manual_id:
        st.session_state.manual_track = manual_id.upper().strip()
        st.rerun()

    st.divider()
    if st.button("🛍️ Browse Books",    use_container_width=True):
        st.switch_page("pages/1_Browse.py")
    if st.button("🤖 AI Assistant",    use_container_width=True):
        st.switch_page("pages/2_AI_Assistant.py")
    if st.button("🏠 Home",            use_container_width=True):
        st.switch_page("app.py")


# ════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="page-title">📦 My Orders</div>', unsafe_allow_html=True)
st.caption("Real-time order tracking — no AI needed here.")

# ── Manual track override ─────────────────────────────────────────────────────
if st.session_state.get("manual_track"):
    order_id = st.session_state.manual_track
    st.markdown(f"### 🔍 Tracking: `{order_id}`")
    with st.spinner("Fetching order..."):
        order = track_order(order_id)

    if order.get("detail") or order.get("error"):
        st.error(f"❌ Order `{order_id}` not found. Please check the Order ID.")
    else:
        render_order_card(order, idx=0)

    if st.button("← Back to All Orders"):
        st.session_state.manual_track = None
        st.rerun()
    st.stop()


# ── Load all orders from conversation memory ──────────────────────────────────
history = get_history(st.session_state.session_id, limit=100)

# Extract all unique ORD- IDs mentioned in assistant messages
seen     = set()
order_ids = []
for h in history:
    if h.get("role") == "assistant":
        content = h.get("content", "")
        import re
        matches = re.findall(r"ORD-\d{5}", content)
        for oid in matches:
            if oid not in seen:
                seen.add(oid)
                order_ids.append(oid)

# Also include last_order_id from session
last = st.session_state.get("last_order_id")
if last and last not in seen:
    order_ids.insert(0, last)

# ── Empty state ───────────────────────────────────────────────────────────────
if not order_ids:
    st.markdown("""
    <div class="empty-state">
        <div style='font-size:56px;'>📭</div>
        <div style='font-size:20px; font-weight:700;
                    color:#e0e0e0; margin:12px 0 8px;'>
            No orders yet
        </div>
        <div style='font-size:14px; color:#606070;'>
            Browse books and place your first order!
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🛍️ Browse Books", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Browse.py")
    with col2:
        if st.button("🤖 Ask AI to recommend", use_container_width=True):
            st.switch_page("pages/2_AI_Assistant.py")
    st.stop()


# ── Tabs: All / Active / Delivered / Returns ──────────────────────────────────
tab_all, tab_active, tab_delivered, tab_returns = st.tabs([
    f"📋 All ({len(order_ids)})",
    "🚚 Active",
    "✅ Delivered",
    "↩️ Returns"
])

# Fetch all orders
with st.spinner("Loading orders..."):
    orders = []
    for oid in order_ids:
        o = track_order(oid)
        if not o.get("error") and not o.get("detail"):
            orders.append(o)

return_statuses  = {"return_initiated","pickup_scheduled","picked_up","refunded"}
active_statuses  = {"confirmed","packed","shipped","out_for_delivery"}
delivered_status = {"delivered"}

active_orders    = [o for o in orders if o.get("status") in active_statuses]
delivered_orders = [o for o in orders if o.get("status") in delivered_status]
return_orders    = [o for o in orders if o.get("status") in return_statuses]

with tab_all:
    if not orders:
        st.info("No orders found.")
    for i, order in enumerate(orders):
        render_order_card(order, idx=i)

with tab_active:
    if not active_orders:
        st.info("No active orders right now.")
    for i, order in enumerate(active_orders):
        render_order_card(order, idx=100 + i)

with tab_delivered:
    if not delivered_orders:
        st.info("No delivered orders yet.")
    for i, order in enumerate(delivered_orders):
        render_order_card(order, idx=200 + i)

with tab_returns:
    if not return_orders:
        st.info("No returns initiated.")
    for i, order in enumerate(return_orders):
        render_order_card(order, idx=300 + i)