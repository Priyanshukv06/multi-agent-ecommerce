from state.schema import EcommerceState
from tools.db_tool import place_order, get_product_by_id

def action_node(state: EcommerceState) -> dict:
    print(f"\n🛒 [ACTION] Processing intent: {state['intent']}")

    intent = state.get("intent")

    # ── Order placement ─────────────────────────────────────────────────────
    if intent == "order":
        product_id = state.get("recommended_product_id")

        if not product_id:
            return {
                "order_status": "failed",
                "final_answer": "❌ No product selected to order. Please ask for a recommendation first.",
                "current_node": "action"
            }

        product = get_product_by_id(product_id)
        order_id = place_order(product_id=product_id, user_id="default_user")

        print(f"  ✅ Order placed: {order_id} for '{product['title']}'")
        return {
            "order_status": "placed",
            "order_id":     order_id,
            "final_answer": (
                f"✅ Order placed successfully!\n\n"
                f"📦 **Order ID:** {order_id}\n"
                f"📚 **Book:** {product['title']}\n"
                f"💰 **Price:** ₹{product['price']}\n"
                f"🚚 **Estimated delivery:** 3-5 business days\n\n"
                f"You can track your order by asking: 'Track order {order_id}'"
            ),
            "current_node": "action"
        }

    # ── Order tracking ───────────────────────────────────────────────────────
    elif intent == "track":
        order_id = None
        # Extract order ID from query e.g. "ORD-00001"
        import re
        match = re.search(r"ORD-\d+", state["user_query"].upper())
        if match:
            order_id = match.group()

        if order_id:
            return {
                "order_status": "tracking",
                "order_id":     order_id,
                "final_answer": (
                    f"📦 **Order Status for {order_id}:**\n\n"
                    f"✅ Status: Confirmed & Processing\n"
                    f"🚚 Estimated delivery: 3-5 business days\n"
                    f"📍 Current location: Warehouse\n\n"
                    f"You'll receive an email update when your order ships."
                ),
                "current_node": "action"
            }
        return {
            "order_status":  "not_found",
            "final_answer":  "❌ Could not find order ID in your query. Please provide your Order ID (e.g. ORD-00001).",
            "current_node":  "action"
        }

    # ── Return request ───────────────────────────────────────────────────────
    elif intent == "return":
        return {
            "order_status": "return_initiated",
            "final_answer": (
                "🔄 **Return Request Initiated**\n\n"
                "To process your return:\n"
                "1. Share your Order ID (e.g. ORD-00001)\n"
                "2. Returns are accepted within 7 days of delivery\n"
                "3. Refund processed in 3-5 business days\n\n"
                "Please share your Order ID to continue."
            ),
            "current_node": "action"
        }

    # ── Fallback ─────────────────────────────────────────────────────────────
    return {
        "order_status": "unknown",
        "final_answer": "I'm not sure how to handle that request. Try asking for a book recommendation!",
        "current_node": "action"
    }
