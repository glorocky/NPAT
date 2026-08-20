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
    
    decision = (
    snapshot.ai.decision
    if snapshot.ai
    else None
)

    option_action = (
        decision.option_action
        if decision
        else "N/A"
    )

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
    
    option_type = (
        snapshot.ai.option_type
        if snapshot.ai
        else "NONE"
    )

    trade_action = (
        snapshot.ai.trade_action
        if snapshot.ai
        else "NO_TRADE"
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
    | Option Action | **{option_action}** |
    | Risk | **{risk}** |
                    """
                )
             
        # -----------------------------------------
        # Actionable Option Direction
        # -----------------------------------------
                
        if trade_action == "BUY_CE":

                st.success(
                    "🎯 TRADE DIRECTION: BUY CALL (CE)"
                )

        elif trade_action == "BUY_PE":

                st.error(
                    "🎯 TRADE DIRECTION: BUY PUT (PE)"
                )

        else:

                st.warning(
                    "🎯 TRADE DIRECTION: NO TRADE"
                )
        
        # -----------------------------------------
        # Right
        # -----------------------------------------

        with right:

            st.markdown("### Reasons")

            for reason in reasons:
                st.markdown(f"✅ {reason}")