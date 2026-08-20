"""
=========================================================
NPAT Professional Trading Dashboard

Paper Trading Summary Component
=========================================================
"""

import streamlit as st

from services.paper_trading_service import (
    PaperTradingService,
)

def render(
    service: PaperTradingService,
):
    """
    Render the Paper Trading Summary.
    """


    summary = service.get_summary()
    
    st.subheader("📈 Paper Trading Summary")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Account Balance",
        f"₹ {summary.account_balance:,.2f}",
    )

    col2.metric(
        "Available Cash",
        f"₹ {summary.available_cash:,.2f}",
    )

    col3.metric(
        "Open Positions",
        summary.open_positions,
    )

    col4.metric(
        "Win Rate",
        f"{summary.win_rate:.2f}%",
    )
    
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Open Trades",
        summary.open_trades,
    )

    col2.metric(
        "Closed Trades",
        summary.closed_trades,
    )

    col3.metric(
        "Today's P&L",
        f"₹ {summary.today_pnl:,.2f}",
    )

    col4.metric(
        "Total P&L",
        f"₹ {summary.total_pnl:,.2f}",
    )