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
    # AI Panel
    # -------------------------------------------------

    ai_container = st.container(
        border=True,
    )

    with ai_container:

        st.subheader("🤖 AI Decision")

        st.info(
            "AI Panel will be connected in Phase 2."
        )

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