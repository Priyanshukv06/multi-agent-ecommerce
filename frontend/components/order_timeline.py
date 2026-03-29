import streamlit as st
from datetime import datetime, timedelta


ORDER_STATES = [
    "confirmed",
    "packed",
    "shipped",
    "out_for_delivery",
    "delivered"
]

RETURN_STATES = [
    "return_initiated",
    "pickup_scheduled",
    "picked_up",
    "refunded"
]

STATE_LABELS = {
    "confirmed":        ("📦", "Order Confirmed"),
    "packed":           ("📫", "Packed"),
    "shipped":          ("🚚", "Shipped"),
    "out_for_delivery": ("🏍️",  "Out for Delivery"),
    "delivered":        ("✅", "Delivered"),
    "cancelled":        ("❌", "Cancelled"),
    "return_initiated": ("🔄", "Return Initiated"),
    "pickup_scheduled": ("📅", "Pickup Scheduled"),
    "picked_up":        ("📤", "Picked Up"),
    "refunded":         ("💰", "Refund Processed"),
}

STATE_MESSAGES = {
    "confirmed":        "Your order has been confirmed and is being processed.",
    "packed":           "Your order has been packed and is ready to ship.",
    "shipped":          "Your order is on its way!",
    "out_for_delivery": "Your order is out for delivery today.",
    "delivered":        "Your order has been delivered. Enjoy your book! 🎉",
    "cancelled":        "This order has been cancelled.",
    "return_initiated": "Return initiated. Pickup will be scheduled within 2 days.",
    "pickup_scheduled": "Pickup has been scheduled.",
    "picked_up":        "Your item has been picked up.",
    "refunded":         "Refund has been processed. Credit in 3-5 business days.",
}


def get_state_index(status: str, is_return: bool = False) -> int:
    states = RETURN_STATES if is_return else ORDER_STATES
    try:
        return states.index(status)
    except ValueError:
        return 0


def order_timeline(order: dict):
    """Render a full order timeline — zero AI calls."""
    status     = order.get("status", "confirmed")
    is_return  = status in RETURN_STATES
    states     = RETURN_STATES if is_return else ORDER_STATES
    current_idx = get_state_index(status, is_return)

    # ── Header ───────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background:#1a1a2e; border:1px solid #0f3460;
                border-radius:12px; padding:16px; margin-bottom:12px;'>
        <div style='font-size:18px; font-weight:700; color:#e94560;'>
            {order.get("title", "")[:50]}
        </div>
        <div style='color:#a0a0b0; font-size:13px; margin-top:4px;'>
            Order ID: <code style='color:#c084fc;'>{order.get("order_id","")}</code>
            &nbsp;|&nbsp; ₹{order.get("price","")}
            &nbsp;|&nbsp; Ordered: {order.get("created_at","")[:10]}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Status message ────────────────────────────────────────────────────────
    msg = STATE_MESSAGES.get(status, "Processing your order.")
    if status == "delivered":
        st.success(f"✅ {msg}")
    elif status == "cancelled":
        st.error(f"❌ {msg}")
    elif is_return:
        st.warning(f"🔄 {msg}")
    else:
        st.info(f"ℹ️ {msg}")

    # ── Timeline steps ────────────────────────────────────────────────────────
    st.markdown("**Order Progress:**")

    for i, state in enumerate(states):
        icon, label = STATE_LABELS.get(state, ("⬜", state))

        if i < current_idx:
            # Completed
            st.markdown(
                f"<div style='padding:6px 0; color:#4caf50;'>"
                f"✅ &nbsp;<b>{label}</b></div>",
                unsafe_allow_html=True
            )
        elif i == current_idx:
            # Current
            st.markdown(
                f"<div style='padding:6px 0; color:#e94560; "
                f"background:#1a1a2e; border-left:3px solid #e94560; "
                f"padding-left:10px; border-radius:4px;'>"
                f"{icon} &nbsp;<b>{label}</b> ← Current</div>",
                unsafe_allow_html=True
            )
        else:
            # Upcoming
            st.markdown(
                f"<div style='padding:6px 0; color:#404060;'>"
                f"⬜ &nbsp;{label}</div>",
                unsafe_allow_html=True
            )

    # ── ETA ───────────────────────────────────────────────────────────────────
    if status not in ("delivered", "cancelled", "refunded"):
        eta = order.get("eta", "")
        if eta:
            st.caption(f"🏁 Estimated Delivery: **{eta}**")