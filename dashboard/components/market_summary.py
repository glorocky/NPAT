"""
=========================================================
NPAT Terminal
Market Summary Component
=========================================================
"""

import streamlit as st


# =====================================================
# Card
# =====================================================

def _card(
    title: str,
    value: str,
    subtitle: str,
):
    """
    Render a compact market summary card.
    """

    st.markdown(
        f"""
        <div style="
            background:#161B22;
            border:1px solid #30363D;
            border-radius:10px;
            padding:14px;
            min-height:95px;
        ">

            <div style="
                color:#8B949E;
                font-size:11px;
                font-weight:600;
                text-transform:uppercase;
            ">
            {title}
            </div>

            <div style="
                color:#F0F6FC;
                font-size:26px;
                font-weight:700;
                margin-top:8px;
            ">
            {value}
            </div>

            <div style="
                color:#58A6FF;
                font-size:12px;
                margin-top:6px;
            ">
            {subtitle}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# =====================================================
# Render
# =====================================================

def render():
    """
    Temporary debug rendering.
    """

    st.success("✅ Market Summary Component Loaded")

    cols = st.columns(6)

    labels = [
        "NIFTY",
        "BANK",
        "VIX",
        "PCR",
        "FUTURES",
        "MARKET",
    ]

    for col, label in zip(cols, labels):
        with col:
            st.metric(
                label=label,
                value="--",
            )