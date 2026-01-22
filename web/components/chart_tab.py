"""Chart tab component."""

import streamlit as st
from chart import display_chart


def render_chart_tab(symbol: str, conv: dict):
    """Render the chart tab for a stock."""
    if conv.get("stock_data"):
        display_chart(symbol, conv["stock_data"], chart_key=f"main_chart_{symbol}")
    else:
        st.info("No chart data available.")
