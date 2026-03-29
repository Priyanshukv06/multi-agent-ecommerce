import streamlit as st
from utils.session import add_to_cart, remove_from_cart, in_cart


def product_card(product: dict, show_buy: bool = True,
                 show_cart: bool = True, compact: bool = False):
    """
    Reusable product card component.
    compact=True → smaller version for lists
    """
    pid = product.get("id")

    with st.container():
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#1a1a2e,#16213e);
                    border:1px solid #0f3460; border-radius:12px;
                    padding:{"12px" if compact else "16px"}; margin:6px 0;'>
            <div style='font-size:{"14px" if compact else "16px"};
                        font-weight:700; color:#e94560;'>
                {product.get("title","")}
            </div>
            <div style='font-size:13px; color:#a0a0b0; margin:3px 0;'>
                ✍️ {product.get("author","")} &nbsp;|&nbsp;
                📂 {product.get("category","").title()}
            </div>
            <div style='margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;'>
                <span style='background:#0f3460;color:#e94560;padding:3px 10px;
                             border-radius:20px;font-weight:700;font-size:14px;'>
                    ₹{product.get("price","")}
                </span>
                <span style='background:#1a3a1a;color:#4caf50;padding:3px 10px;
                             border-radius:20px;font-size:13px;'>
                    ⭐ {product.get("rating","")}/5
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if not compact:
            with st.expander("📄 Description"):
                st.caption(product.get("description", ""))

        if show_buy or show_cart:
            cols = st.columns(2) if (show_buy and show_cart) else st.columns(1)

            if show_cart:
                with cols[0] if (show_buy and show_cart) else cols[0]:
                    already = in_cart(pid)
                    if already:
                        if st.button(
                            "🛒 In Cart", key=f"cart_{pid}",
                            use_container_width=True, type="secondary"
                        ):
                            remove_from_cart(pid)
                            st.rerun()
                    else:
                        if st.button(
                            "➕ Add to Cart", key=f"cart_{pid}",
                            use_container_width=True
                        ):
                            add_to_cart(product)
                            st.rerun()

            if show_buy:
                btn_col = cols[1] if (show_buy and show_cart) else cols[0]
                with btn_col:
                    if st.button(
                        "⚡ Buy Now", key=f"buy_{pid}",
                        use_container_width=True, type="primary"
                    ):
                        st.session_state[f"buy_now_{pid}"] = True
                        st.rerun()