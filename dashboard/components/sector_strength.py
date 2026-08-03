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
from dashboard.widgets.card import compact_kpi_card


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
            # ---------------------------------
            # Friendly Classification
            # ---------------------------------

            classification = (
                sector.classification
                .replace("_", " ")
                .title()
            )
            
            classification_icons = {
                "Strong Bullish": "🟢 Strong Bullish",
                "Bullish": "🟢 Bullish",
                "Neutral": "🟡 Neutral",
                "Bearish": "🔴 Bearish",
                "Strong Bearish": "🔴 Strong Bearish",
            }

            classification = classification_icons.get(
                classification,
                classification,
            )            

            left, right = st.columns(2)

            with left:

                compact_kpi_card(
                    "Strength Score",
                    f"{sector.strength_score:.1f}",
                )

                compact_kpi_card(
                    "Breadth",
                    f"{sector.breadth_pct:.1f}%",
                )

                compact_kpi_card(
                    "Classification",
                    sector.classification,
                )

            with right:

                compact_kpi_card(
                    "Avg Change",
                    f"{sector.average_change_pct:.2f}%",
                )

                compact_kpi_card(
                    "Leader",
                    sector.strongest_symbol,
                )

                compact_kpi_card(
                    "Laggard",
                    sector.weakest_symbol,
                )