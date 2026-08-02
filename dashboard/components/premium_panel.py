"""
=========================================================
NPAT Premium Panel
=========================================================

Displays live Forward Premium analytics.

Data Source:
    DashboardSnapshot.atm_call_premium
    DashboardSnapshot.atm_put_premium
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
    Render the Premium Analysis panel.
    """

    st.subheader("💰 Premium Analysis")

    call = snapshot.atm_call_premium
    put = snapshot.atm_put_premium

    if call is None or put is None:

        st.warning(
            "Premium data not available."
        )

        return

    left, right = st.columns(2)

    # -------------------------------------------------
    # Call Premium
    # -------------------------------------------------

    with left:

        st.metric(
            "Call Market",
            f"{call.market_premium:.2f}",
        )

        st.metric(
            "Call Theo",
            f"{call.forward_bs_premium:.2f}",
        )

        st.metric(
            "Call Difference",
            f"{call.forward_difference_pct:.2f}%",
        )

    # -------------------------------------------------
    # Put Premium
    # -------------------------------------------------

    with right:

        st.metric(
            "Put Market",
            f"{put.market_premium:.2f}",
        )

        st.metric(
            "Put Theo",
            f"{put.forward_bs_premium:.2f}",
        )

        st.metric(
            "Put Difference",
            f"{put.forward_difference_pct:.2f}%",
        )

    st.divider()

    st.metric(
        "Relative Richness",
        f"{snapshot.relative_richness:.2f}%",
    )