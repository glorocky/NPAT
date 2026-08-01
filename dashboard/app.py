"""
=========================================================
NPAT Professional Trading Dashboard
=========================================================
"""

import streamlit as st

from layout import render
from theme import load_theme


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
# Render Dashboard
# -------------------------------------------------

render()