"""
=========================================================
NPAT Professional Trading Dashboard

Paper Trading Statistics Component
=========================================================
"""

import streamlit as st

from services.paper_trading_service import (
    PaperTradingService,
)


def render(
    service: PaperTradingService,
) -> None:
    """
    Render paper trading performance statistics.
    """


    statistics = service.get_statistics()

    st.subheader("📊 Paper Trading Statistics")
    
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Total Trades",
        statistics.total_trades,
    )

    col2.metric(
        "Winning Trades",
        statistics.winning_trades,
    )

    col3.metric(
        "Losing Trades",
        statistics.losing_trades,
    )

    col4.metric(
        "Breakeven Trades",
        statistics.breakeven_trades,
    )

    col5.metric(
        "Win Rate",
        f"{statistics.win_rate:.2f}%",
    )
 
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric(
        "Gross Profit",
        f"₹ {statistics.gross_profit:,.2f}",
    )

    col2.metric(
        "Gross Loss",
        f"₹ {statistics.gross_loss:,.2f}",
    )

    col3.metric(
        "Net Profit",
        f"₹ {statistics.net_profit:,.2f}",
    )

    col4.metric(
        "Profit Factor",
        f"{statistics.profit_factor:.2f}",
    )

    col5.metric(
        "Expectancy",
        f"₹ {statistics.expectancy:,.2f}",
    )

    col6.metric(
        "Max Drawdown",
        f"₹ {statistics.max_drawdown:,.2f}",
    )
    
    
    # =========================================================
    # Equity Curve
    # =========================================================

    equity_curve = service.get_equity_curve()

    if equity_curve:
        st.subheader("📈 Paper Trading Equity Curve")

        st.line_chart(
            equity_curve,
            x_label="Trade",
            y_label="Cumulative P&L (₹)",
        )
    else:
        st.info(
            "No closed paper trades available "
            "for equity curve."
        )