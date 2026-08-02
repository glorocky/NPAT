"""
=========================================================
NPAT Professional Trading Dashboard
=========================================================
"""

import streamlit as st

from dashboard.layout import render
from dashboard.theme import load_theme

from services.bootstrap import (
    create_market_service,
    get_default_symbol,
    get_default_exchange,
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

# -------------------------------------------------
# Load Dashboard Data
# -------------------------------------------------

snapshot = service.get_dashboard_snapshot(
    symbol=get_default_symbol(),
    exchange=get_default_exchange(),
)

# -------------------------------------------------
# Render Dashboard
# -------------------------------------------------

render(snapshot)


