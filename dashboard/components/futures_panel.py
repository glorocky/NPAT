"""
=========================================================
NPAT Futures Panel
=========================================================

Displays live Futures analytics.

Data Source:
    DashboardSnapshot.futures
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
    Render the Futures Analysis panel.
    """

    st.subheader("📈 Futures Analysis")

    futures = snapshot.futures

    if futures is None:

        st.warning(
            "Futures data not available."
        )

        return

    left, right = st.columns(2)

    # -------------------------------------------------
    # Price Context
    # -------------------------------------------------

    with left:

        compact_kpi_card(
            "Futures Price",
            f"{futures.futures_price:,.2f}",
        )

        compact_kpi_card(
            "Spot Price",
            f"{futures.spot_price:,.2f}",
        )

        compact_kpi_card(
            "Basis",
            f"{futures.basis:.2f}",
        )

        compact_kpi_card(
            "Basis %",
            f"{futures.basis_pct:.2f}%",
        )

    # -------------------------------------------------
    # Positioning
    # -------------------------------------------------

    with right:

        compact_kpi_card(
            "Positioning",
            futures.positioning,
        )

        compact_kpi_card(
            "OI Change",
            f"{futures.oi_change_pct:.2f}%",
        )

        compact_kpi_card(
            "Current OI",
            f"{futures.current_oi:,}",
        )

        compact_kpi_card(
            "Previous OI",
            f"{futures.previous_oi:,}",
        )

    st.divider()

    bottom_left, bottom_right = st.columns(2)

    with bottom_left:

        compact_kpi_card(
            "Volume",
            f"{futures.volume:,}",
        )

        compact_kpi_card(
            "Buy Quantity",
            f"{futures.total_buy_quantity:,}",
        )

    with bottom_right:

        compact_kpi_card(
            "Sell Quantity",
            f"{futures.total_sell_quantity:,}",
        )

        compact_kpi_card(
            "Qty Imbalance",
            f"{futures.quantity_imbalance_pct:.2f}%",
        )