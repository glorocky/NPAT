"""
=========================================================
NPAT Professional Trading Dashboard

Paper Trading Controls
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
    Render manual paper trading controls.
    """


    st.subheader("🎮 Paper Trading Controls")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        symbol = st.text_input(
            "Symbol",
            value="NIFTY",
        ).strip().upper()

    with col2:
        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=65,
            step=1,
        )

    with col3:
        price = st.number_input(
            "Price",
            min_value=0.0,
            value=25000.0,
            step=0.05,
        )

    with col4:
        stop_loss = st.number_input(
            "Stop Loss",
            min_value=0.0,
            value=0.0,
            step=0.05,
        )

    target = st.number_input(
        "Target",
        min_value=0.0,
        value=0.0,
        step=0.05,
    )

    buy_col, sell_col = st.columns(2)

    with buy_col:

        if st.button(
            "🟢 BUY",
            width="stretch",
        ):
            try:

                trade = service.buy(
                    symbol=symbol,
                    quantity=int(quantity),
                    price=float(price),
                    stop_loss=float(stop_loss),
                    target=float(target),
                )

                st.success(
                    f"BUY opened: {trade.symbol} "
                    f"× {trade.quantity} @ "
                    f"{trade.entry_price:,.2f}"
                )
                
            except RuntimeError as exc:

                st.error(str(exc))

    with sell_col:

        if st.button(
            "🔴 SELL",
            width="stretch",
        ):
            try:

                trade = service.sell(
                    symbol=symbol,
                    quantity=int(quantity),
                    price=float(price),
                    stop_loss=float(stop_loss),
                    target=float(target),
                )

                st.success(
                    f"SELL opened: {trade.symbol} "
                    f"× {trade.quantity} @ "
                    f"{trade.entry_price:,.2f}"
                )
                
            except RuntimeError as exc:

                st.error(str(exc))

    open_trades = service.get_open_positions()

    if not open_trades:

        st.info("No open trades available to close.")
        return

    st.markdown("### Close Open Trade")

    trade_options = {
        (
            f"{trade.symbol} | "
            f"{trade.side.value} | "
            f"{trade.quantity} | "
            f"Entry {trade.entry_price:,.2f}"
        ): trade
        for trade in open_trades
    }

    selected_label = st.selectbox(
    "Select Trade",
    list(trade_options.keys()),
    key="paper_close_trade_select",
    )

    selected_trade = trade_options[selected_label]

    close_price = st.number_input(
        "Exit Price",
        min_value=0.0,
        value=float(selected_trade.current_price),
        step=0.05,
        key=f"close_price_{selected_trade.trade_id}",
    )

    if st.button(
        "⚪ CLOSE TRADE",
        width="stretch",
    ):
        try:

            closed_trade = service.close_trade(
                trade_id=selected_trade.trade_id,
                price=float(close_price),
            )

            st.success(
                f"Trade closed: "
                f"{closed_trade.symbol} | "
                f"P&L ₹{closed_trade.realized_pnl:,.2f}"
            )
        except (RuntimeError, ValueError) as exc:

            st.error(str(exc))