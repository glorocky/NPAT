"""
=========================================================
NPAT Professional Trading Dashboard
=========================================================
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from layout import render
from theme import load_theme
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
# Create Services
# -------------------------------------------------

service = create_market_service()

paper_service = PaperTradingService()

# -------------------------------------------------
# Load Dashboard Data
# -------------------------------------------------

snapshot = service.get_dashboard_snapshot(
    symbol=get_default_symbol(),
    exchange=get_default_exchange(),
)

# -------------------------------------------------
# Update Paper Trading Market Prices
# -------------------------------------------------

paper_service.update_open_market_prices(
    lambda symbol, exchange: service.get_quote(
        symbol=symbol,
        exchange=exchange,
    )
)


# -------------------------------------------------
# Render Dashboard
# -------------------------------------------------

render(
    snapshot,
    service,
    paper_service,
    )