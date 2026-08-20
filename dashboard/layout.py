
"""
=========================================================
NPAT Dashboard Layout
=========================================================

Responsible for arranging dashboard components.

This module does NOT perform:
- Provider calls
- Analytics
- AI calculations

It only renders the dashboard layout.
=========================================================
"""
import streamlit as st

from core.dashboard_models import DashboardSnapshot
from dashboard import header
from dashboard import sidebar

from dashboard.components.market_summary import (
    render as render_market_summary,
)

from dashboard.components.ai_panel import (
    render as render_ai_panel,
)
from dashboard.components.greeks_panel import (
    render as render_greeks_panel,
)
from dashboard.components.premium_panel import (
    render as render_premium_panel,
)
from dashboard.components.futures_panel import (
    render as render_futures_panel,
)
from dashboard.components.vix_panel import (
    render as render_vix_panel,
)

from dashboard.components.sector_strength import (
    render as render_sector_strength,
)
from dashboard.components.heatmap import (
    render as render_heatmap,
)
from dashboard.components.option_chain import (
    render as render_option_chain,
)

from dashboard.components.paper_summary import (
    render as render_paper_summary,
)
from dashboard.components.paper_positions import (
    render as render_paper_positions,
)
from dashboard.components.paper_statistics import (
    render as render_paper_statistics,
)

from dashboard.components.paper_history import (
    render as render_paper_history,
)
from dashboard.components.paper_controls import (
    render as render_paper_controls,
)

from services.paper_trading_service import (
    PaperTradingService,
)


def render(
    snapshot: DashboardSnapshot,
    market_service,
    paper_service: PaperTradingService,
    settings: dict,
) -> dict:
    """
    Render the complete dashboard layout.

    Returns
    -------
    dict
        User settings from the sidebar.
    """


    # -------------------------------------------------
    # Header
    # -------------------------------------------------

    header.render()
    
    # -------------------------------------------------
    # Market Summary
    # -------------------------------------------------

    render_market_summary(snapshot)

    st.write("")

    # -------------------------------------------------
    # AI Panel
    # -------------------------------------------------

    render_ai_panel(snapshot)
    
    # -------------------------------------------------
    # Paper Trading Controls
    # -------------------------------------------------

    paper_controls = st.container(
        border=True,
    )

    with paper_controls:

        render_paper_controls(
            paper_service,
        )
    
    # -------------------------------------------------
    # Paper Trading Summary
    # -------------------------------------------------

    paper_summary = st.container(
        border=True,
    )

    with paper_summary:

        render_paper_summary(
            paper_service,
        )
    
    # -------------------------------------------------
    # Paper Trading Positions
    # -------------------------------------------------

    paper_positions = st.container(
        border=True,
    )

    with paper_positions:

        render_paper_positions(
            paper_service,
        )
        
    # -------------------------------------------------
    # Paper Trading Statistics
    # -------------------------------------------------

    paper_statistics = st.container(
        border=True,
    )

    with paper_statistics:

        render_paper_statistics(
             paper_service,
        )
        
    # -------------------------------------------------
    # Paper Trading History
    # -------------------------------------------------

    paper_history = st.container(
        border=True,
    )

    with paper_history:

        render_paper_history(
            paper_service,
        )

    # -------------------------------------------------
    # Greeks / Premium
    # -------------------------------------------------

    left, right = st.columns(2)

    # -------------------------------------------------
    # Greeks
    # -------------------------------------------------

    with left:

        render_greeks_panel(snapshot)

    # -------------------------------------------------
    # Premium
    # -------------------------------------------------

    with right:

         render_premium_panel(snapshot)
         
    # -------------------------------------------------
    # Futures / VIX
    # -------------------------------------------------

    left, right = st.columns(2)

    with left:

        render_futures_panel(snapshot)

    with right:
        
         render_vix_panel(snapshot)


    # -------------------------------------------------
    # Sector / Heatmap
    # -------------------------------------------------

    left, right = st.columns(2)

    with left:
        
         render_sector_strength(snapshot)
        

    with right:
        
        render_heatmap(snapshot)


    # -------------------------------------------------
    # Option Chain
    # -------------------------------------------------

    option_chain = st.container(
        border=True,
    )

    with option_chain:
        
        render_option_chain(snapshot)
        
    return settings