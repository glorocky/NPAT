"""
=========================================================
NPAT Dashboard Widgets
Simple Table
=========================================================
"""

import streamlit as st


# =====================================================
# Table Header
# =====================================================

def table_header(
    columns: list[str],
) -> None:
    """
    Render a standard table header.
    """

    cols = st.columns(len(columns))

    for col, title in zip(cols, columns):

        with col:

            st.markdown(f"**{title}**")

    st.divider()


# =====================================================
# Table Row
# =====================================================

def table_row(
    values: list[str],
) -> None:
    """
    Render one table row.
    """

    cols = st.columns(len(values))

    for col, value in zip(cols, values):

        with col:

            st.write(value)