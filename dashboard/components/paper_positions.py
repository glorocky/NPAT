"""
=========================================================
NPAT Professional Trading Dashboard

Paper Trading Open Positions Component
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
    Render currently open paper trading positions.
    """


    positions = service.get_open_positions()

    st.subheader("📌 Paper Trading Positions")

    if not positions:
        st.info("No open paper trading positions.")
        return

    rows = []

    for trade in positions:
        rows.append(
            {
                "Symbol": trade.symbol,
                "Side": trade.side.value,
                "Quantity": trade.quantity,
                "Entry": trade.entry_price,
                "LTP": trade.current_price,
                "Stop Loss": trade.stop_loss,
                "Target": trade.target,
                "Unrealized P&L": trade.unrealized_pnl,
                "Status": trade.status.value,
            }
        )

    st.dataframe(
        rows,
        width="stretch",
        hide_index=True,
    )