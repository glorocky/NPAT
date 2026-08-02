"""
=========================================================
NPAT Greeks Panel
=========================================================

Displays live Greeks analytics for the ATM option window.

Data Source:
    DashboardSnapshot.greeks_summary
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
    Render the live Greeks summary panel.
    """

    st.subheader("📊 Greeks Summary")

    greeks = snapshot.greeks_summary

    if greeks is None:

        st.warning(
            "Greeks data not available."
        )

        return

    left, right = st.columns(2)

    # -------------------------------------------------
    # Left Column
    # -------------------------------------------------

    with left:

        st.metric(
            "ATM Strike",
            greeks.atm_strike,
        )

        st.metric(
            "Call Delta",
            f"{greeks.atm_call_delta:.4f}",
        )

        st.metric(
            "Put Delta",
            f"{greeks.atm_put_delta:.4f}",
        )

        st.metric(
            "Delta Balance",
            f"{greeks.delta_balance:.4f}",
        )

        st.metric(
            "Call IV",
            f"{greeks.atm_call_iv:.2f}%",
        )

        st.metric(
            "Put IV",
            f"{greeks.atm_put_iv:.2f}%",
        )

    # -------------------------------------------------
    # Right Column
    # -------------------------------------------------

    with right:

        st.metric(
            "IV Skew",
            f"{greeks.iv_skew:.2f}",
        )

        st.metric(
            "Highest Gamma Strike",
            greeks.highest_gamma_strike,
        )

        st.metric(
            "Highest Gamma",
            f"{greeks.highest_gamma:.4f}",
        )

        st.metric(
            "Total Theta",
            f"{greeks.total_theta:.2f}",
        )

        st.metric(
            "Total Vega",
            f"{greeks.total_vega:.2f}",
        )