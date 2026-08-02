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
import header
import sidebar
from components.market_summary import (
    render as render_market_summary,
)

from components.ai_panel import (
    render as render_ai_panel,
)


def render() -> dict:
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

    render_market_summary()

    st.write("")

    # -------------------------------------------------
    # AI Panel
    # -------------------------------------------------

    render_ai_panel()

    # -------------------------------------------------
    # Greeks / Premium
    # -------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.container(border=True)

        st.subheader("📊 Greeks Summary")

        st.write("Coming soon...")

    with right:

        st.container(border=True)

        st.subheader("💰 Premium Analysis")

        st.write("Coming soon...")

    # -------------------------------------------------
    # Futures / VIX
    # -------------------------------------------------

    left, right = st.columns(2)

    with left:

        st.container(border=True)

        st.subheader("📈 Futures Analysis")

        st.write("Coming soon...")

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