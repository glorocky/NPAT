"""
=========================================================
NPAT Terminal
Market Summary Component
=========================================================
"""

import streamlit as st
from core.dashboard_models import DashboardSnapshot


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

def render(
    snapshot: DashboardSnapshot,
):
    """
    Render the live market summary.
    """

    cols = st.columns(6)

    # -------------------------------------------------
    # NIFTY
    # -------------------------------------------------

    with cols[0]:

        st.metric(
            label="NIFTY",
            value=f"{snapshot.market.spot_price:,.2f}",
            delta=f"ATM {snapshot.market.atm_strike}",
        )

    # -------------------------------------------------
    # PCR
    # -------------------------------------------------

    with cols[1]:

        st.metric(
            label="PCR",
            value=f"{snapshot.market.pcr:.2f}",
            delta=snapshot.market.expiry,
        )

    # -------------------------------------------------
    # INDIA VIX
    # -------------------------------------------------

    with cols[2]:

        st.metric(
            label="VIX",
            value=f"{snapshot.india_vix:.2f}",
            delta="India VIX",
        )

    # -------------------------------------------------
    # FUTURES
    # -------------------------------------------------

    with cols[3]:

        st.metric(
            label="FUTURES",
            value="LIVE",
            delta="Coming Next",
        )

    # -------------------------------------------------
    # MARKET
    # -------------------------------------------------

    with cols[4]:

        st.metric(
            label="MARKET",
            value=snapshot.market_regime.regime,
            delta=f"{snapshot.ai.confidence:.1f}% Confidence",
        )

    # -------------------------------------------------
    # LAST UPDATE
    # -------------------------------------------------

    with cols[5]:

        st.metric(
            label="UPDATED",
            value=snapshot.market.timestamp.strftime("%H:%M:%S"),
            delta=snapshot.market.symbol,
        )

