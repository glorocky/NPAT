"""
=========================================================
NPAT Professional Trading Dashboard
=========================================================
"""

import streamlit as st

from dashboard.layout import render
from dashboard.theme import load_theme
from dashboard import sidebar

from services.bootstrap import (
    create_market_service,
    get_default_symbol,
    get_default_exchange,
)
from services.paper_trading_service import (
    PaperTradingService,
)

# -------------------------------------------------
# Streamlit Page Configuration
# -------------------------------------------------

st.set_page_config(
    page_title="NPAT Professional Trading Terminal",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -------------------------------------------------
# Load Theme
# -------------------------------------------------

load_theme()

# -------------------------------------------------
# Sidebar
# -------------------------------------------------

settings = sidebar.render()

# -------------------------------------------------
# Create Services
# -------------------------------------------------

if "market_service" not in st.session_state:
    st.session_state.market_service = (
        create_market_service()
    )

if "paper_trading_service" not in st.session_state:
    st.session_state.paper_trading_service = (
        PaperTradingService()
    )

service = st.session_state.market_service

paper_service = (
    st.session_state.paper_trading_service
)

# -------------------------------------------------
# Refreshable Dashboard
# -------------------------------------------------

@st.fragment(
    run_every=(
        settings["refresh_interval"]
        if settings["auto_refresh"]
        else None
    )
)
def render_live_dashboard() -> None:
    """
    Refresh market data, paper trading prices,
    and dashboard UI at the configured interval.
    """

    snapshot = service.get_dashboard_snapshot(
        symbol=get_default_symbol(),
        exchange=get_default_exchange(),
    )

    paper_service.update_open_market_prices(
        lambda symbol, exchange: service.get_quote(
            symbol=symbol,
            exchange=exchange,
        )
    )

    render(
        snapshot,
        service,
        paper_service,
        settings,
    )


render_live_dashboard()

