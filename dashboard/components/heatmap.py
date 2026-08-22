"""Selected-index heatmap: gainers/losers always follow the sidebar index."""
from __future__ import annotations
import streamlit as st
from core.dashboard_models import DashboardSnapshot


def render(snapshot: DashboardSnapshot) -> None:
    symbol = snapshot.market.symbol if snapshot.market else "INDEX"
    st.subheader(f"🔥 {symbol} Constituents")
    summary = snapshot.heatmap_summary
    heatmap = snapshot.heatmap or []
    if summary is None or not heatmap:
        st.info(f"No constituent data available for {symbol}.")
        return
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Gainers", summary.gainers)
    c2.metric("Losers", summary.losers)
    c3.metric("A/D", f"{summary.advance_decline_ratio:.2f}")
    c4.metric("Avg %", f"{summary.average_change_pct:+.2f}%")
    gainers = sorted((x for x in heatmap if x.change_pct > 0), key=lambda x: x.change_pct, reverse=True)[:10]
    losers = sorted((x for x in heatmap if x.change_pct < 0), key=lambda x: x.change_pct)[:10]
    left, right = st.columns(2)
    with left:
        st.markdown("**🟢 Top Gainers**")
        st.dataframe([{"Symbol": x.symbol, "Change %": f"+{x.change_pct:.2f}", "Sector": x.sector} for x in gainers], hide_index=True, width="stretch", height=300)
    with right:
        st.markdown("**🔴 Top Losers**")
        st.dataframe([{"Symbol": x.symbol, "Change %": f"{x.change_pct:.2f}", "Sector": x.sector} for x in losers], hide_index=True, width="stretch", height=300)
