"""
=========================================================
NPAT Dashboard Widgets
Section Header
=========================================================
"""

import streamlit as st


# =====================================================
# Section Header
# =====================================================

def section(
    title: str,
) -> None:
    """
    Render a standardized section header.
    """

    st.markdown(
        f"""
<div style="
margin-top:18px;
margin-bottom:12px;
font-size:22px;
font-weight:700;
color:#F0F6FC;
">
{title}
</div>
""",
        unsafe_allow_html=True,
    )

    st.divider()