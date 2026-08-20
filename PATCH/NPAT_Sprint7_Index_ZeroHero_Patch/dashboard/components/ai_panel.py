"""NPAT AI Hero Panel."""

import streamlit as st
from core.dashboard_models import DashboardSnapshot


def render(snapshot: DashboardSnapshot) -> None:
    ai = snapshot.ai
    signal = ai.signal if ai else "N/A"
    confidence = f"{ai.confidence:.2f}%" if ai else "N/A"
    regime = snapshot.market_regime.regime if snapshot.market_regime else "N/A"
    prediction = ai.prediction.direction if ai and ai.prediction else "N/A"
    recommendation = ai.recommendation if ai else None

    option_action = recommendation.action if recommendation else "N/A"
    option_type = recommendation.option_type if recommendation else "NONE"
    strike = recommendation.strike_price if recommendation else "-"
    entry = f"₹{recommendation.entry_price:.2f}" if recommendation else "-"
    risk = "LOW" if ai and ai.confidence >= 70 else "MEDIUM"
    reasons = ai.reasons if ai else ("AI not available.",)

    container = st.container(border=True)
    with container:
        st.subheader("🤖 AI Market Decision")
        left, right = st.columns([2, 1])

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
| Option Type | **{option_type}** |
| Selected Strike | **{strike}** |
| Entry Premium | **{entry}** |
| Risk | **{risk}** |
                """
            )

            if option_action == "BUY CALL":
                st.success(
                    f"🎯 BUY CALL (CE) — {snapshot.market.symbol} {strike} @ {entry}"
                )
            elif option_action == "BUY PUT":
                st.error(
                    f"🎯 BUY PUT (PE) — {snapshot.market.symbol} {strike} @ {entry}"
                )
            else:
                st.warning("🎯 NO TRADE")

        with right:
            st.markdown("### Reasons")
            for reason in reasons:
                st.markdown(f"✅ {reason}")
