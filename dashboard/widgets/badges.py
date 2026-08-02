"""
=========================================================
NPAT Dashboard Widgets
Status Badge
=========================================================
"""

import streamlit as st


# =====================================================
# Badge
# =====================================================

def badge(
    text: str,
    color: str = "#238636",
) -> None:
    """
    Render a colored status badge.
    """

    st.markdown(
        f"""
<span style="
background:{color};
padding:4px 10px;
border-radius:12px;
color:white;
font-size:12px;
font-weight:600;
">
{text}
</span>
""",
        unsafe_allow_html=True,
    )