"""
=========================================================
NPAT Professional Trading Dashboard

Paper Trading History Component
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
    Render paper trading history.
    """

    trades = service.get_trade_history()

    st.subheader("📜 Paper Trading History")

    if not trades:
        st.info("No paper trading history available.")
        return

    rows = []

    for trade in trades:

        rows.append(
            {
                "Symbol": trade.symbol,
                "Side": trade.side.value,
                "Quantity": trade.quantity,
                "Entry": trade.entry_price,
                "Exit": trade.exit_price,
                "Realized P&L": trade.realized_pnl,
                "Status": trade.status.value,
                "Exit Reason": (
                        trade.exit_reason.value
                    if trade.exit_reason
                    else "-"
                ),
                     "Entry Time": trade.entry_time.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                "Exit Time": (
                    trade.exit_time.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                    if trade.exit_time
                    else "-"
                ),
            }
        )

    st.dataframe(
        rows,
        width="stretch",
        hide_index=True,
    )
    
    st.divider()

    st.markdown("### Trade Lifecycle")

    trade_options = {
        (
            f"{trade.symbol} | "
            f"{trade.side.value} | "
            f"{trade.quantity} | "
            f"Entry {trade.entry_price:,.2f}"
        ): trade.trade_id
        for trade in trades
    }

    selected_label = st.selectbox(
        "Select Trade",
        list(trade_options.keys()),
        key="paper_history_trade_select",
    )

    selected_trade_id = trade_options[selected_label]

    events = service.get_trade_events(
        trade_id=selected_trade_id,
    )

    if not events:

        st.info(
            "No lifecycle events available for this trade."
        )

    else:

        event_rows = []

        for event in events:

            event_rows.append(
                {
                    "Timestamp": event.timestamp.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "Event": event.event,
                    "Description": event.description,
                }
            )

        st.dataframe(
            event_rows,
            width="stretch",
            hide_index=True,
        )