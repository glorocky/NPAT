
"""
=========================================================
NPAT Dashboard Layout
=========================================================

Responsible for arranging dashboard components.

This module does NOT perform:
- Provider calls
- Analytics
- AI calculations

It only renders the dashboard layout.
=========================================================
"""
import streamlit as st

from core.dashboard_models import DashboardSnapshot
from dashboard import header
from dashboard import sidebar

from dashboard.components.market_summary import (
    render as render_market_summary,
)

from dashboard.components.ai_panel import (
    render as render_ai_panel,
)
from dashboard.components.greeks_panel import (
    render as render_greeks_panel,
)
from dashboard.components.premium_panel import (
    render as render_premium_panel,
)
from dashboard.components.futures_panel import (
    render as render_futures_panel,
)


def render(
    snapshot: DashboardSnapshot,
) -> dict:
    """
    Render the complete dashboard layout.

    Returns
    -------
    dict
        User settings from the sidebar.
    """

    # -------------------------------------------------
    # Sidebar
    # -------------------------------------------------

    settings = sidebar.render()

    # -------------------------------------------------
    # Header
    # -------------------------------------------------

    header.render()
    
    # -------------------------------------------------
    # Market Summary
    # -------------------------------------------------

    render_market_summary(snapshot)

    st.write("")

    # -------------------------------------------------
    # AI Panel
    # -------------------------------------------------

    render_ai_panel(snapshot)

    # -------------------------------------------------
    # Greeks / Premium
    # -------------------------------------------------

    left, right = st.columns(2)

    # -------------------------------------------------
    # Greeks
    # -------------------------------------------------

    with left:

        render_greeks_panel(snapshot)

    # -------------------------------------------------
    # Premium
    # -------------------------------------------------

    with right:

         render_premium_panel(snapshot)
         
    # -------------------------------------------------
    # Futures / VIX
    # -------------------------------------------------

    left, right = st.columns(2)

    with left:

        render_futures_panel(snapshot)

    with right:

        st.container(border=True)

        st.subheader("🌡 India VIX")

        st.write("Coming soon...")

    # -------------------------------------------------
    # Sector / Heatmap
    # -------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.container(border=True)

        st.subheader("🏦 Sector Strength")

        st.write("Coming soon...")

    with right:

        st.container(border=True)

        st.subheader("🔥 Market Heatmap")

        st.write("Coming soon...")

    # -------------------------------------------------
    # Option Chain
    # -------------------------------------------------

    option_chain = st.container(
        border=True,
    )

    with option_chain:

        st.subheader("📋 Live Option Chain")

        st.write(
            "Option Chain will appear here."
        )

    return settings