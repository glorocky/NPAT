"""NPAT Dashboard Sidebar."""

from __future__ import annotations

import streamlit as st


INDEX_CONFIG: dict[str, dict[str, str]] = {
    "NIFTY": {"exchange": "NSE", "expiry": "Weekly - Tuesday"},
    "BANKNIFTY": {"exchange": "NSE", "expiry": "Monthly - Tuesday"},
    "FINNIFTY": {"exchange": "NSE", "expiry": "Monthly - Tuesday"},
    "MIDCPNIFTY": {"exchange": "NSE", "expiry": "Monthly - Tuesday"},
    "SENSEX": {"exchange": "BSE", "expiry": "Weekly - Thursday"},
    "BANKEX": {"exchange": "BSE", "expiry": "Monthly - Thursday"},
}


def render() -> dict:
    st.sidebar.title("⚙ Dashboard")

    symbol = st.sidebar.selectbox(
        "Underlying",
        list(INDEX_CONFIG.keys()),
        key="npat_underlying",
    )

    config = INDEX_CONFIG[symbol]
    exchange = config["exchange"]

    st.sidebar.caption(
        f"Exchange: {exchange}  •  Expiry: {config['expiry']}"
    )

    auto_refresh = st.sidebar.checkbox("Auto Refresh", value=True)

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
    st.sidebar.write("Version : v1.0.0")
    st.sidebar.write("Sprint  : 12 — Final")

    return {
        "symbol": symbol,
        "exchange": exchange,
        "expiry_rule": config["expiry"],
        "auto_refresh": auto_refresh,
        "refresh_interval": refresh_interval,
    }
