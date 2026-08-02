"""
=========================================================
NPAT AI Hero Panel
=========================================================
"""

import streamlit as st

from core.dashboard_models import DashboardSnapshot


# =====================================================
# Render
# =====================================================

def render(snapshot: DashboardSnapshot) -> None:
    """
    Render the AI Hero Card.

    Mock data is used for Sprint 4.
    This component will later receive data from AIService.
    """

# -------------------------------------------------
# Live AI Data
# -------------------------------------------------

    signal = snapshot.ai.signal if snapshot.ai else "N/A"

    confidence = (
        f"{snapshot.ai.confidence:.2f}%"
        if snapshot.ai
        else "N/A"
    )

    regime = (
        snapshot.market_regime.regime
        if snapshot.market_regime
        else "N/A"
    )

    prediction = (
        snapshot.ai.prediction.direction
        if snapshot.ai and snapshot.ai.prediction
        else "N/A"
    )

    risk = (
        "LOW"
        if snapshot.ai and snapshot.ai.confidence >= 70
        else "MEDIUM"
    )

    reasons = (
        snapshot.ai.reasons
        if snapshot.ai
        else ["AI not available."]
    )

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