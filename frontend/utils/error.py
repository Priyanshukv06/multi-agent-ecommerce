import streamlit as st


def show_api_error(result: dict | list, context: str = "") -> bool:
    """
    Check if an API result contains an error and display it cleanly.

    Usage:
        result = place_order(pid, session_id)
        if show_api_error(result, "placing order"):
            return   # stop further processing

    Returns True if error was found and shown, False if result is clean.
    """
    if not isinstance(result, dict):
        return False

    error   = result.get("error")
    detail  = result.get("detail")
    fields  = result.get("fields")

    if not error:
        return False

    # ── Categorize error and show appropriate UI ──────────────────────────────
    msg = detail or error

    if "not running" in msg.lower() or "connection" in msg.lower():
        st.error(
            "🔌 **API Server Offline**\n\n"
            "Start it with:\n```\nuvicorn api.main:app --reload --port 8000\n```"
        )

    elif "timed out" in msg.lower() or "timeout" in msg.lower():
        st.warning(
            "⏱️ **Request Timed Out**\n\n"
            "The AI pipeline is taking too long. Please try again."
        )

    elif "not found" in msg.lower() or "404" in str(result):
        label = f" while {context}" if context else ""
        st.warning(f"🔍 **Not Found{label}**: {msg}")

    elif "validation" in msg.lower() or fields:
        st.error(
            f"⚠️ **Invalid Request**\n\n"
            + ("\n".join(f"- {f}" for f in fields) if fields else msg)
        )

    elif "expired" in msg.lower():
        st.warning(f"⏰ **{msg}**")

    elif "cancelled" in msg.lower():
        st.info(f"ℹ️ {msg}")

    else:
        label = f" while {context}" if context else ""
        st.error(f"❌ **Error{label}**: {msg}")

    return True


def show_connection_banner():
    """
    Show a persistent warning at top of page if API is unreachable.
    Call once at the top of any page that makes API calls.
    """
    from utils.api import health_check
    result = health_check()
    if isinstance(result, dict) and result.get("error"):
        st.warning(
            "⚠️ **API server is not responding.** "
            "Some features may not work. "
            "Run: `uvicorn api.main:app --reload --port 8000`",
            icon="🔌"
        )
        return False
    return True