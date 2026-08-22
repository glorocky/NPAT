"""Compact sector-strength view designed to avoid vertical dashboard bloat."""
from __future__ import annotations

import streamlit as st
from core.dashboard_models import DashboardSnapshot


def render(snapshot: DashboardSnapshot) -> None:
    st.subheader("🏦 Sector Strength")
    sectors = snapshot.sector_strength or []
    if not sectors:
        st.info("Sector data not available.")
        return
    rows = []
    for rank, sector in enumerate(sectors, 1):
        cls = sector.classification.replace("_", " ").title()
        rows.append({
            "#": rank,
            "Sector": sector.sector,
            "Score": round(sector.strength_score, 1),
            "Breadth": f"{sector.breadth_pct:.1f}%",
            "Avg %": f"{sector.average_change_pct:+.2f}%",
            "Leader": sector.strongest_symbol,
            "Laggard": sector.weakest_symbol,
            "View": cls,
        })
    st.dataframe(rows, width="stretch", hide_index=True, height=min(360, 45 + 35 * len(rows)))
    strongest = sectors[0]
    weakest = sectors[-1]
    a, b = st.columns(2)
    a.metric("Strongest", strongest.sector, f"{strongest.strength_score:.1f}")
    b.metric("Weakest", weakest.sector, f"{weakest.strength_score:.1f}")
