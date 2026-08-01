"""
=========================================================
NPAT Professional Dashboard Theme
=========================================================

Centralized theme configuration for the Streamlit UI.

All dashboard modules should use this file for:
- Colors
- CSS
- Typography
- Card styling
- Status colors

=========================================================
"""

from pathlib import Path

import streamlit as st


# =====================================================
# Color Palette
# =====================================================

BACKGROUND = "#0F1116"
CARD = "#1A1D24"
BORDER = "#2D323C"

TEXT = "#F3F6FA"
TEXT_SECONDARY = "#A8B0BF"

SUCCESS = "#00C853"
DANGER = "#FF5252"
WARNING = "#FFB300"
INFO = "#42A5F5"
ACCENT = "#7C4DFF"


# =====================================================
# Status Colors
# =====================================================

SIGNAL_COLORS = {
    "STRONG_BUY": SUCCESS,
    "BUY": "#4CAF50",
    "NEUTRAL": WARNING,
    "SELL": "#FB8C00",
    "STRONG_SELL": DANGER,
}

REGIME_COLORS = {
    "STRONG_BULLISH": SUCCESS,
    "BULLISH": "#4CAF50",
    "NEUTRAL": WARNING,
    "BEARISH": "#FB8C00",
    "STRONG_BEARISH": DANGER,
}


# =====================================================
# Helpers
# =====================================================

def get_signal_color(signal: str) -> str:
    """Return color for AI signal."""
    return SIGNAL_COLORS.get(signal.upper(), TEXT)


def get_regime_color(regime: str) -> str:
    """Return color for market regime."""
    return REGIME_COLORS.get(regime.upper(), TEXT)


# =====================================================
# CSS Loader
# =====================================================

def load_theme() -> None:
    """
    Apply NPAT dashboard styling.
    """

    css_file = (
        Path(__file__)
        .parent
        / "assets"
        / "custom.css"
    )

    if css_file.exists():

        st.markdown(
            f"<style>{css_file.read_text()}</style>",
            unsafe_allow_html=True,
        )