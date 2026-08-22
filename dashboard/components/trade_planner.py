"""AI stock/futures trade planner with protective option hedging."""

from __future__ import annotations

import math
import streamlit as st

from core.dashboard_models import DashboardSnapshot


def render(snapshot: DashboardSnapshot, market_service) -> None:
    st.subheader("🧠 AI Stock / Futures Trade Planner")
    st.caption("Directional plan with a protective option hedge. Analysis only; no orders are placed here.")

    with st.form("npat_trade_planner"):
        left, mid, right = st.columns([1, 1, 1])
        with left:
            asset_type = st.selectbox("Instrument", ["STOCK", "FUTURE"])
        with mid:
            symbol = st.text_input("Symbol", value="RELIANCE").strip().upper()
        with right:
            quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
        submitted = st.form_submit_button("Analyze AI Trade", use_container_width=True)

    if submitted:
        if not symbol:
            st.error("Enter a valid trading symbol.")
            return
        try:
            idea = market_service.get_hedged_trade_idea(
                asset_type=asset_type,
                symbol=symbol,
                quantity=int(quantity),
                market_score=(snapshot.market_regime.regime_score if snapshot.market_regime else 0.0),
                exchange="NSE",
            )
            st.session_state.npat_trade_idea = idea
        except Exception as exc:
            st.session_state.npat_trade_idea = None
            st.error(f"Trade analysis unavailable: {exc}")

    idea = st.session_state.get("npat_trade_idea")
    if idea is None:
        st.info("Enter a stock or futures symbol and run AI analysis.")
        return

    action = idea.action
    if action.startswith("BUY"):
        st.success(f"🎯 {action} — {idea.symbol} @ ₹{idea.entry_price:,.2f}")
    elif action.startswith("SELL"):
        st.error(f"🎯 {action} — {idea.symbol} @ ₹{idea.entry_price:,.2f}")
    else:
        st.warning(f"⏸ {action} — {idea.symbol}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("AI Signal", idea.signal)
    c2.metric("Confidence", f"{idea.confidence:.1f}%")
    c3.metric("Score", f"{idea.score:+.1f}")
    c4.metric("Quantity", f"{idea.quantity:,}")

    if idea.hedge:
        hedge = idea.hedge
        st.markdown(
            f"**🛡 Hedge:** {hedge.action} {hedge.option_type} "
            f"{hedge.strike_price:,} @ ₹{hedge.entry_price:,.2f} "
            f"({hedge.expiry}) · Qty {hedge.quantity:,}"
        )
    else:
        st.warning("Protective option hedge could not be selected from the available option chain.")

    with st.expander("Why NPAT chose this plan", expanded=True):
        for reason in idea.reasons:
            st.markdown(f"✅ {reason}")
