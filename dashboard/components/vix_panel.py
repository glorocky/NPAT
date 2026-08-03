"""
=========================================================
NPAT India VIX Panel
=========================================================

Displays live India VIX analytics.

Data Source:
    DashboardSnapshot.vix_analysis
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
    Render the India VIX panel.
    """

    st.subheader("🌡 India VIX")

    vix = snapshot.vix_analysis

    if vix is None:

        st.warning(
            "India VIX data not available."
        )

        return

    left, right = st.columns(2)

    # -------------------------------------------------
    # VIX / Expected Range
    # -------------------------------------------------

    with left:

        compact_kpi_card(
            "India VIX",
            f"{vix.india_vix:.2f}",
        )

        compact_kpi_card(
            "Expected Move",
            f"{vix.expected_move_points:.2f}",
        )

        compact_kpi_card(
            "Expected Range",
            f"{vix.expected_lower:.2f} - {vix.expected_upper:.2f}",
        )

        compact_kpi_card(
            "Expected Move %",
            f"{vix.expected_move_pct:.2f}%",
        )

    # -------------------------------------------------
    # Today's Progress
    # -------------------------------------------------

    with right:

        compact_kpi_card(
            "Actual Range",
            f"{vix.actual_range:.2f}",
        )

        compact_kpi_card(
            "Range Used",
            f"{vix.range_achieved_pct:.2f}%",
        )

        compact_kpi_card(
            "Upside Remaining",
            f"{vix.upside_remaining:.2f}",
        )

        compact_kpi_card(
            "Downside Remaining",
            f"{vix.downside_remaining:.2f}",
        )