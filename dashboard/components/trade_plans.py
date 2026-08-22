"""AI candidate plans for index futures and individual stocks with protective hedges."""
from __future__ import annotations
import streamlit as st


def _show(plan, title: str) -> None:
    if plan is None:
        st.info("No plan available.")
        return
    st.markdown(f"### {title} — {plan.action}")
    if plan.status == "NO_TRADE":
        st.warning("NO TRADE")
        for r in plan.rationale:
            st.caption(f"• {r}")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Entry", f"₹{plan.entry_price:,.2f}")
    c2.metric("Stop", f"₹{plan.stop_loss:,.2f}")
    c3.metric("Target", f"₹{plan.target:,.2f}")
    c4.metric("Confidence", f"{plan.confidence:.0f}%")
    if plan.hedge:
        h = plan.hedge
        st.success(f"🛡 Hedge: BUY {h.option_type} {h.strike or ''} @ ₹{h.entry_price:,.2f} {h.trading_symbol or ''}")
    else:
        st.warning("🛡 Hedge contract unavailable from current provider data — do not assume protection.")
    for r in plan.rationale:
        st.caption(f"• {r}")
    st.caption("Paper/review recommendation only. No live order is submitted by this module.")


def render(snapshot) -> None:
    st.subheader("🧠 AI Trade Plans")
    a, b = st.columns(2)
    with a:
        _show(snapshot.future_trade_plan, "Future")
    with b:
        _show(snapshot.stock_trade_plan, "Individual Stock")
