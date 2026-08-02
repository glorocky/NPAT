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

        st.metric(
            "Futures Price",
            f"{futures.futures_price:,.2f}",
        )

        st.metric(
            "Spot Price",
            f"{futures.spot_price:,.2f}",
        )

        st.metric(
            "Basis",
            f"{futures.basis:.2f}",
        )

        st.metric(
            "Basis %",
            f"{futures.basis_pct:.2f}%",
        )

    # -------------------------------------------------
    # Positioning
    # -------------------------------------------------

    with right:

        st.metric(
            "Positioning",
            futures.positioning,
        )

        st.metric(
            "OI Change",
            f"{futures.oi_change_pct:.2f}%",
        )

        st.metric(
            "Current OI",
            f"{futures.current_oi:,}",
        )

        st.metric(
            "Previous OI",
            f"{futures.previous_oi:,}",
        )

    st.divider()

    bottom_left, bottom_right = st.columns(2)

    with bottom_left:

        st.metric(
            "Volume",
            f"{futures.volume:,}",
        )

        st.metric(
            "Buy Quantity",
            f"{futures.total_buy_quantity:,}",
        )

    with bottom_right:

        st.metric(
            "Sell Quantity",
            f"{futures.total_sell_quantity:,}",
        )

        st.metric(
            "Qty Imbalance",
            f"{futures.quantity_imbalance_pct:.2f}%",
        )