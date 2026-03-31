import re
from state.schema import EcommerceState
from tools.db_tool import (
    place_order, get_order, get_user_orders,
    initiate_return, cancel_order, get_product_by_id
)


def extract_order_id(text: str) -> str | None:
    match = re.search(r"ORD-\d+", text.upper())
    return match.group() if match else None


def extract_return_reason(text: str) -> str:
    text_lower = text.lower()
    if any(w in text_lower for w in ["damage", "broken", "defect"]):
        return "Damaged or defective product"
    if any(w in text_lower for w in ["wrong", "incorrect", "different"]):
        return "Wrong item received"
    if any(w in text_lower for w in ["not needed", "changed mind", "mistake"]):
        return "No longer needed"
    return "Customer requested return"


def handle_order(state: EcommerceState) -> dict:
    product_id = state.get("recommended_product_id")
    user_id    = state.get("user_id", "default_user")

    if not product_id:
        return {
            "order_status": "failed",
            "final_answer": (
                "❌ No product selected to order.\n\n"
                "Please ask for a recommendation first, then say 'buy it' or 'place order'."
            ),
            "current_node": "action"
        }

    product  = get_product_by_id(product_id)
    order_id = place_order(product_id=product_id, user_id=user_id)

    print(f"  ✅ Order placed: {order_id} → '{product.title}'")

    return {
        "order_status": "confirmed",
        "order_id":     order_id,
        "final_answer": (
            f"✅ **Order Placed Successfully!**\n\n"
            f"📦 **Order ID:** `{order_id}`\n"
            f"📚 **Book:** {product.title}\n"
            f"✍️  **Author:** {product.author}\n"
            f"💰 **Price:** ₹{product.price}\n"
            f"⭐ **Rating:** {product.rating}/5\n\n"
            f"🚚 **Estimated Delivery:** 3–5 business days\n\n"
            f"You can track your order anytime by asking:\n"
            f"> *'Track order {order_id}'*"
        ),
        "current_node": "action"
    }


def handle_track(state: EcommerceState) -> dict:
    query    = state["user_query"]
    user_id  = state.get("user_id", "default_user")
    order_id = extract_order_id(query)

    if not order_id:
        orders = get_user_orders(user_id)
        if not orders:
            return {
                "order_status": "no_orders",
                "final_answer": (
                    "📭 You have no orders yet.\n\n"
                    "Ask for a book recommendation and place an order to get started!"
                ),
                "current_node": "action"
            }
        orders_text = "\n".join([
            f"• `{o['order_id']}` — {o['title'][:35]} | ₹{o['price']} | {o['status'].upper()}"
            for o in orders
        ])
        return {
            "order_status": "listed",
            "final_answer": (
                f"📦 **Your Recent Orders:**\n\n{orders_text}\n\n"
                f"To track a specific order, ask:\n> *'Track order ORD-XXXXX'*"
            ),
            "current_node": "action"
        }

    order = get_order(order_id)
    if not order:
        return {
            "order_status": "not_found",
            "final_answer": (
                f"❌ Order `{order_id}` not found.\n\n"
                f"Please check your Order ID and try again.\n"
                f"To see all your orders, ask: *'Show my orders'*"
            ),
            "current_node": "action"
        }

    print(f"  ✅ Tracking: {order_id} → {order['delivery_status']}")

    return {
        "order_status": order["status"],
        "order_id":     order_id,
        "final_answer": (
            f"📦 **Order Status — `{order_id}`**\n\n"
            f"📚 **Book:** {order['title']}\n"
            f"✍️  **Author:** {order['author']}\n"
            f"💰 **Price:** ₹{order['price']}\n\n"
            f"🚦 **Status:** {order['delivery_status']}\n"
            f"📍 **Location:** {order['location']}\n"
            f"📅 **Ordered On:** {order['created_at'][:10]}\n"
            f"🏁 **Estimated Delivery:** {order['eta']}\n\n"
            f"Need help? Ask: *'Return order {order_id}'*"
        ),
        "current_node": "action"
    }


def handle_return(state: EcommerceState) -> dict:
    query    = state["user_query"]
    user_id  = state.get("user_id", "default_user")
    order_id = extract_order_id(query)
    reason   = extract_return_reason(query)

    if not order_id:
        orders = get_user_orders(user_id)
        if orders:
            latest   = orders[0]
            order_id = latest["order_id"]
            print(f"  ℹ️  No order ID in query — using latest: {order_id}")
        else:
            return {
                "order_status": "no_orders",
                "final_answer": (
                    "❌ No orders found to return.\n\n"
                    "You need to have a placed order before initiating a return."
                ),
                "current_node": "action"
            }

    result = initiate_return(order_id, reason, user_id)

    if result is None:
        return {
            "order_status": "return_failed",
            "final_answer": (
                f"❌ Order `{order_id}` not found in your account.\n\n"
                f"Please provide a valid Order ID."
            ),
            "current_node": "action"
        }

    if result == "EXPIRED":
        return {
            "order_status": "return_expired",
            "final_answer": (
                f"⏰ **Return Window Expired**\n\n"
                f"Order `{order_id}` is outside the 7-day return window.\n"
                f"Unfortunately, we cannot process this return.\n\n"
                f"For exceptions, please contact support."
            ),
            "current_node": "action"
        }

    if result == "ALREADY_CANCELLED":
        return {
            "order_status": "already_cancelled",
            "final_answer": f"ℹ️ Order `{order_id}` was already cancelled.",
            "current_node": "action"
        }

    print(f"  ✅ Return initiated: {result} for {order_id}")

    return {
        "order_status": "return_initiated",
        "order_id":     order_id,
        "final_answer": (
            f"🔄 **Return Initiated Successfully!**\n\n"
            f"📋 **Return ID:** `{result}`\n"
            f"📦 **Order ID:** `{order_id}`\n"
            f"📝 **Reason:** {reason}\n\n"
            f"**Next Steps:**\n"
            f"1. Pack the book securely\n"
            f"2. A pickup will be scheduled within 2 business days\n"
            f"3. Refund processed in 3–5 business days after pickup\n\n"
            f"Track your return with: *'Track return {result}'*"
        ),
        "current_node": "action"
    }


def action_node(state: EcommerceState) -> dict:
    intent = state.get("intent", "")
    print(f"\n🛒 [ACTION] Processing intent: {intent.upper()}")

    if intent == "order":
        return handle_order(state)
    elif intent == "track":
        return handle_track(state)
    elif intent == "return":
        return handle_return(state)
    else:
        return {
            "order_status": "unknown",
            "final_answer": (
                "I'm not sure how to handle that request.\n\n"
                "Here's what I can do:\n"
                "• **Recommend** a book → *'Suggest a Python book under ₹800'*\n"
                "• **Place order** → *'Buy it'* (after a recommendation)\n"
                "• **Track order** → *'Track order ORD-00001'*\n"
                "• **Return order** → *'Return order ORD-00001'*"
            ),
            "current_node": "action"
        }