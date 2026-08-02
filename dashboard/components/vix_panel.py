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

        st.metric(
            "India VIX",
            f"{vix.india_vix:.2f}",
        )

        st.metric(
            "Expected Move",
            f"{vix.expected_move_points:.2f}",
        )

        st.metric(
            "Expected Range",
            f"{vix.expected_lower:.2f} - {vix.expected_upper:.2f}",
        )

        st.metric(
            "Expected Move %",
            f"{vix.expected_move_pct:.2f}%",
        )

    # -------------------------------------------------
    # Today's Progress
    # -------------------------------------------------

    with right:

        st.metric(
            "Actual Range",
            f"{vix.actual_range:.2f}",
        )

        st.metric(
            "Range Used",
            f"{vix.range_achieved_pct:.2f}%",
        )

        st.metric(
            "Upside Remaining",
            f"{vix.upside_remaining:.2f}",
        )

        st.metric(
            "Downside Remaining",
            f"{vix.downside_remaining:.2f}",
        )