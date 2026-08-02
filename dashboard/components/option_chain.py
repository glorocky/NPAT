"""
=========================================================
NPAT Live Option Chain
=========================================================

Displays ATM-focused live option chain.

Data Source:
    DashboardSnapshot.market.option_chain
=========================================================
"""

import streamlit as st

from core.dashboard_models import DashboardSnapshot


# =====================================================
# Render
# =====================================================

def render(
    snapshot: DashboardSnapshot,
) -> None:
    """
    Render live option chain.
    """

    st.subheader("📋 Live Option Chain")

    market = snapshot.market

    option_chain = market.option_chain

    if not option_chain:

        st.warning(
            "Option chain not available."
        )

        return

    atm = market.atm_strike

    # -----------------------------------------
    # Show ATM ±5 strikes
    # -----------------------------------------

    option_chain = sorted(
        option_chain,
        key=lambda x: x.strike_price,
    )

    atm_index = next(
        (
            i
            for i, item in enumerate(option_chain)
            if item.strike_price == atm
        ),
        len(option_chain) // 2,
    )

    start = max(0, atm_index - 5)
    end = min(len(option_chain), atm_index + 6)

    window = option_chain[start:end]

    st.caption(
        f"ATM Strike : {atm}"
    )

    headers = st.columns(7)

    headers[0].markdown("**Call OI**")
    headers[1].markdown("**Call LTP**")
    headers[2].markdown("**Call IV**")
    headers[3].markdown("**Strike**")
    headers[4].markdown("**Put IV**")
    headers[5].markdown("**Put LTP**")
    headers[6].markdown("**Put OI**")

    st.divider()

    for option in window:

        cols = st.columns(7)

        cols[0].write(f"{option.call_oi:,}")
        cols[1].write(f"{option.call_ltp:.2f}")
        cols[2].write(f"{option.call_iv:.2f}")

        if option.strike_price == atm:

            cols[3].markdown(
                f"**🟨 {option.strike_price}**"
            )

        else:

            cols[3].write(option.strike_price)

        cols[4].write(f"{option.put_iv:.2f}")
        cols[5].write(f"{option.put_ltp:.2f}")
        cols[6].write(f"{option.put_oi:,}")