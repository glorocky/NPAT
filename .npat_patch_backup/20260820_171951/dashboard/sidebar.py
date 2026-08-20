"""
=========================================================
NPAT Dashboard Sidebar
=========================================================

Sidebar controls for the NPAT Professional Dashboard.
"""

import streamlit as st


def render() -> dict:
    """
    Render sidebar controls.

    Returns
    -------
    dict
        Dashboard settings selected by the user.
    """

    st.sidebar.title("⚙ Dashboard")

    symbol = st.sidebar.selectbox(
        "Underlying",
        [
            "NIFTY",
            "BANKNIFTY",
            "FINNIFTY",
        ],
    )

    auto_refresh = st.sidebar.checkbox(
        "Auto Refresh",
        value=True,
    )

    refresh_interval = st.sidebar.slider(
        "Refresh Interval (seconds)",
        min_value=5,
        max_value=60,
        value=10,
        step=5,
    )

    st.sidebar.divider()

    st.sidebar.subheader("Provider")

    st.sidebar.success("🟢 Groww Connected")

    st.sidebar.divider()

    st.sidebar.subheader("Application")

    st.sidebar.write("Version : v0.4.0")
    st.sidebar.write("Sprint  : 4")

    return {
        "symbol": symbol,
        "auto_refresh": auto_refresh,
        "refresh_interval": refresh_interval,
    }