"""Stock page component - main page for viewing a stock."""

import streamlit as st
from stock import get_stock_logo_url

from .chart_tab import render_chart_tab
from .chat_tab import render_chat_tab
from .competitors_tab import render_competitors_tab
from .technical_tab import render_technical_tab


def render_stock_page(symbol: str):
    """Render the page for a specific stock."""
    conv = st.session_state.stock_conversations.get(symbol, {"messages": [], "stock_data": None})
    
    # Header with logo
    st.markdown(
        f'<div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">'
        f'<img src="{get_stock_logo_url(symbol)}" width="45" style="border-radius: 6px;">'
        f'<h3 style="margin: 0;">{symbol}</h3>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Check beginner mode - hide technical tab if enabled
    beginner_mode = st.session_state.get("beginner_mode", True)
    
    if beginner_mode:
        # Simplified tabs for beginners
        tab1, tab2, tab3 = st.tabs(["Chart", "Chat", "Competitors"])
        
        with tab1:
            render_chart_tab(symbol, conv)
        
        with tab2:
            render_chat_tab(symbol, conv)
        
        with tab3:
            render_competitors_tab(symbol)
    else:
        # Full tabs including technical analysis
        tab1, tab2, tab3, tab4 = st.tabs(["Chart", "Chat", "Technical", "Competitors"])
        
        with tab1:
            render_chart_tab(symbol, conv)
        
        with tab2:
            render_chat_tab(symbol, conv)
        
        with tab3:
            render_technical_tab(symbol, conv)
        
        with tab4:
            render_competitors_tab(symbol)
