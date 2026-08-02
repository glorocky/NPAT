"""
=========================================================
NPAT AI Hero Panel
=========================================================
"""

import streamlit as st


# =====================================================
# Render
# =====================================================

def render() -> None:
    """
    Render the AI Hero Card.

    Mock data is used for Sprint 4.
    This component will later receive data from AIService.
    """

    signal = "🟢 STRONG BUY"
    confidence = "93.08%"
    regime = "BULLISH"
    prediction = "STRONG_BULLISH"
    risk = "LOW"

    reasons = [
        "Futures show Short Covering.",
        "Premium analytics are Bullish.",
        "Greeks indicate Positive Delta.",
        "India VIX remains stable.",
    ]

    container = st.container(border=True)

    with container:

        st.subheader("🤖 AI Market Decision")

        left, right = st.columns([2, 1])

        # -----------------------------------------
        # Left
        # -----------------------------------------

        with left:

            st.markdown(
                f"""
### {signal}

| Metric | Value |
|--------|-------|
| Confidence | **{confidence}** |
| Market Regime | **{regime}** |
| Prediction | **{prediction}** |
| Risk | **{risk}** |
                """
            )

        # -----------------------------------------
        # Right
        # -----------------------------------------

        with right:

            st.markdown("### Reasons")

            for reason in reasons:
                st.markdown(f"✅ {reason}")