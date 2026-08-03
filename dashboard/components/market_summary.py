"""
=========================================================
NPAT Terminal
Market Summary Component
=========================================================
"""

import streamlit as st
from core.dashboard_models import DashboardSnapshot
from dashboard.widgets.card import kpi_card


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

            kpi_card(
                title="NIFTY",
                value=f"{snapshot.market.spot_price:,.2f}",
                subtitle=f"ATM {snapshot.market.atm_strike}",
            )

        # -------------------------------------------------
        # PCR
        # -------------------------------------------------

        with cols[1]:

            kpi_card(
                title="PCR",
                value=f"{snapshot.market.pcr:.2f}",
                subtitle=snapshot.market.expiry,
            )

        # -------------------------------------------------
        # INDIA VIX
        # -------------------------------------------------

        with cols[2]:

            kpi_card(
                title="INDIA VIX",
                value=f"{snapshot.india_vix:.2f}",
                subtitle="Volatility Index",
            )

        # -------------------------------------------------
        # FUTURES
        # -------------------------------------------------

        with cols[3]:

            futures = snapshot.futures

            if futures:

                basis = f"{futures.basis:+.2f}"

                kpi_card(
                    title="FUTURES",
                    value=f"{futures.futures_price:,.2f}",
                    subtitle=f"Basis {basis}",
                )

            else:

                kpi_card(
                    title="FUTURES",
                    value="--",
                    subtitle="No Data",
                )

        # -------------------------------------------------
        # MARKET
        # -------------------------------------------------

        with cols[4]:

            regime = (
                snapshot.market_regime.regime
                if snapshot.market_regime
                else "UNKNOWN"
            )

            confidence = (
                f"{snapshot.ai.confidence:.1f}% Confidence"
                if snapshot.ai
                else "No AI"
            )

            kpi_card(
                title="MARKET",
                value=regime,
                subtitle=confidence,
            )

        # -------------------------------------------------
        # LAST UPDATE
        # -------------------------------------------------

        with cols[5]:

            kpi_card(
                title="UPDATED",
                value=snapshot.market.timestamp.strftime("%H:%M:%S"),
                subtitle=snapshot.market.symbol,
            )

