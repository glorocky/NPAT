"""
=========================================================
NPAT Market Heatmap
=========================================================

Displays market breadth and top movers.

Data Source:
    DashboardSnapshot.heatmap
=========================================================
"""

import streamlit as st

from core.dashboard_models import DashboardSnapshot


# =====================================================
# Render
# =====================================================

def render(
    snapshot: DashboardSnapshot,
) -> None:
    """
    Render Market Heatmap.
    """

    st.subheader("🔥 Market Heatmap")

    summary = snapshot.heatmap_summary
    heatmap = snapshot.heatmap

    if summary is None or not heatmap:

        st.warning(
            "Heatmap data not available."
        )

        return

    # -------------------------------------------------
    # Summary
    # -------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Gainers", summary.gainers)
    c2.metric("Losers", summary.losers)
    c3.metric("A/D Ratio", f"{summary.advance_decline_ratio:.2f}")
    c4.metric("Avg Change", f"{summary.average_change_pct:.2f}%")

    st.write("")

    # -------------------------------------------------
    # Top Gainers
    # -------------------------------------------------

    gainers = sorted(
        [s for s in heatmap if s.change_pct > 0],
        key=lambda x: x.change_pct,
        reverse=True,
    )[:10]

    st.markdown("### 🟢 Top Gainers")

    for stock in gainers:

        left, right = st.columns([3, 1])

        with left:

            st.write(
                f"▲ **{stock.symbol}** ({stock.sector})"
            )

        with right:

            st.write(
                f"**+{stock.change_pct:.2f}%**"
            )

    st.divider()

    # -------------------------------------------------
    # Top Losers
    # -------------------------------------------------

    losers = sorted(
        [s for s in heatmap if s.change_pct < 0],
        key=lambda x: x.change_pct,
    )[:10]

    st.markdown("### 🔴 Top Losers")

    for stock in losers:

        left, right = st.columns([3, 1])

        with left:

            st.write(
                f"▼ **{stock.symbol}** ({stock.sector})"
            )

        with right:

            st.write(
                f"**{stock.change_pct:.2f}%**"
            )