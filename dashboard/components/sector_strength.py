"""
=========================================================
NPAT Sector Strength Panel
=========================================================

Displays ranked sector strength.

Data Source:
    DashboardSnapshot.sector_strength
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
    Render Sector Strength panel.
    """

    st.subheader("🏦 Sector Strength")

    sectors = snapshot.sector_strength

    if not sectors:

        st.warning(
            "Sector data not available."
        )

        return

    medals = [
        "🥇",
        "🥈",
        "🥉",
    ]

    for index, sector in enumerate(sectors):

        badge = (
            medals[index]
            if index < 3
            else "📊"
        )

        with st.container(border=True):

            st.markdown(
                f"### {badge} {sector.sector}"
            )

            left, right = st.columns(2)

            with left:

                st.metric(
                    "Strength Score",
                    f"{sector.strength_score:.1f}",
                )

                st.metric(
                    "Breadth",
                    f"{sector.breadth_pct:.1f}%",
                )

                st.metric(
                    "Classification",
                    sector.classification,
                )

            with right:

                st.metric(
                    "Avg Change",
                    f"{sector.average_change_pct:.2f}%",
                )

                st.metric(
                    "Leader",
                    sector.strongest_symbol,
                )

                st.metric(
                    "Laggard",
                    sector.weakest_symbol,
                )