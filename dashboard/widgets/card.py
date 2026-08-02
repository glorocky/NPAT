"""
=========================================================
NPAT Dashboard Widgets
KPI Card
=========================================================
"""

import streamlit as st


# =====================================================
# KPI Card
# =====================================================

def kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
) -> None:
    """
    Render a professional KPI card.
    """

    st.markdown(
        f"""
<div style="
background:#161B22;
border:1px solid #30363D;
border-radius:12px;
padding:16px;
min-height:110px;
">

<div style="
color:#8B949E;
font-size:12px;
font-weight:600;
text-transform:uppercase;
">
{title}
</div>

<div style="
margin-top:10px;
font-size:28px;
font-weight:700;
color:#F0F6FC;
">
{value}
</div>

<div style="
margin-top:8px;
font-size:13px;
color:#58A6FF;
">
{subtitle}
</div>

</div>
""",
        unsafe_allow_html=True,
    )