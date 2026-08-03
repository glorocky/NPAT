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
from dashboard.widgets.card import compact_kpi_card


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

        compact_kpi_card(
            "ATM Strike",
            str(greeks.atm_strike),
        )

        compact_kpi_card(
            "Call Delta",
            f"{greeks.atm_call_delta:.4f}",
        )

        compact_kpi_card(
            "Put Delta",
            f"{greeks.atm_put_delta:.4f}",
        )

        compact_kpi_card(
            "Delta Balance",
            f"{greeks.delta_balance:.4f}",
        )

        compact_kpi_card(
            "Call IV",
            f"{greeks.atm_call_iv:.2f}%",
        )

        compact_kpi_card(
            "Put IV",
            f"{greeks.atm_put_iv:.2f}%",
        )
    # -------------------------------------------------
    # Right Column
    # -------------------------------------------------

    with right:

        compact_kpi_card(
            "IV Skew",
            f"{greeks.iv_skew:.2f}",
        )

        compact_kpi_card(
            "Highest Gamma Strike",
            greeks.highest_gamma_strike,
        )

        compact_kpi_card(
            "Highest Gamma",
            f"{greeks.highest_gamma:.4f}",
        )

        compact_kpi_card(
            "Total Theta",
            f"{greeks.total_theta:.2f}",
        )

        compact_kpi_card(
            "Total Vega",
            f"{greeks.total_vega:.2f}",
        )