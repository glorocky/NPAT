"""
=========================================================
NPAT Terminal
Professional Header
=========================================================
"""

from datetime import datetime

import streamlit as st


# =====================================================
# Header
# =====================================================

def render() -> None:
    """
    Renders the professional NPAT terminal header.
    """

    left, middle, right = st.columns(
        [5, 2, 2]
    )

    # -------------------------------------------------
    # Left
    # -------------------------------------------------

    with left:

        st.markdown(
            """
            <h2 style="
                margin-bottom:0;
                padding-bottom:0;
                color:#F0F6FC;
                font-weight:700;
            ">
            NPAT Terminal
            </h2>

            <div style="
                color:#8B949E;
                font-size:13px;
                margin-top:-6px;
            ">
            AI Powered Options Trading Terminal
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------
    # Middle
    # -------------------------------------------------

    with middle:

        st.markdown(
            """
            <div style="
                text-align:center;
                margin-top:8px;
                font-size:14px;
            ">
            <span style="color:#3FB950;">
            ●
            </span>

            Groww Connected
            </div>
            """,
            unsafe_allow_html=True,
        )

    # -------------------------------------------------
    # Right
    # -------------------------------------------------

    with right:

        current_time = datetime.now().strftime(
            "%H:%M:%S"
        )

        st.markdown(
            f"""
            <div style="
                text-align:right;
                margin-top:8px;
                color:#58A6FF;
                font-size:15px;
                font-weight:600;
            ">
            {current_time}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()