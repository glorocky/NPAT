"""
=========================================================
NPAT Dashboard Header
=========================================================
"""

from datetime import datetime

import streamlit as st


def render() -> None:
    """
    Render the dashboard header.
    """

    st.title("📈 NPAT Professional Trading Terminal")

    st.caption(
        "AI Powered | Live Market Analytics | Groww Provider"
    )

    st.divider()

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

    with col1:
        st.metric(
            "NIFTY",
            "--",
        )

    with col2:
        st.metric(
            "BANKNIFTY",
            "--",
        )

    with col3:
        st.metric(
            "INDIA VIX",
            "--",
        )

    with col4:
        st.metric(
            "PCR",
            "--",
        )

    with col5:
        st.metric(
            "FUTURES",
            "--",
        )

    with col6:
        st.metric(
            "MARKET",
            "Closed",
        )

    with col7:
        st.metric(
            "UPDATED",
            datetime.now().strftime("%H:%M:%S"),
        )

    st.divider()