import streamlit as st
from stock import get_stock_logo_url, get_stock_history
from .state import clear_all_state
from history import save_conversations


def render_sidebar():
    """Render the sidebar with stock navigation."""
    with st.sidebar:
        st.markdown(
            '<h1 style="margin-top: -50px;">📈 AI Stock Analyzer</h1>',
            unsafe_allow_html=True
        )
        
        st.markdown(
            '<h3 style="margin-bottom: -1rem;">Your Stocks</h3>',
            unsafe_allow_html=True
        )
        st.markdown('<hr style="margin: 0 0 0.5rem 0;">', unsafe_allow_html=True)
        # Show expanders for each stock that has been discussed
        if st.session_state.stock_conversations:
            for symbol in st.session_state.stock_conversations.keys():
                _render_stock_item(symbol)
        else:
            st.caption("No stocks analyzed yet. Ask a question to get started!")
        
        if st.button("➕ New Chat", use_container_width=True):
            st.session_state.selected_stock = None
            st.session_state.selected_view = "chat"
            st.rerun()
        
        if st.button("🔄 Refresh All Stocks", use_container_width=True):
            _refresh_all_stocks()
            st.rerun()
        
        st.divider()
        
        if st.button("🗑️ Clear All", use_container_width=True):
            clear_all_state()
            st.rerun()


def _render_stock_item(symbol: str):
    """Render a single stock item in the sidebar."""
    # Check if analysis is running for this stock
    is_analyzing = symbol in st.session_state.active_threads
    analyzing_badge = " (thinking...)" if is_analyzing else ""
    
    # Build expander label with logo and symbol
    expander_label = f"![logo]({get_stock_logo_url(symbol)}) **{symbol}**{analyzing_badge}"
    
    with st.expander(expander_label, expanded=(st.session_state.selected_stock == symbol)):
        # Chart button
        if st.button("📊 Chart", key=f"chart_btn_{symbol}", use_container_width=True):
            st.session_state.selected_stock = symbol
            st.session_state.selected_view = "chart"
            st.rerun()
        
        # Chat button
        if st.button("💬 Chat", key=f"chat_btn_{symbol}", use_container_width=True):
            st.session_state.selected_stock = symbol
            st.session_state.selected_view = "chat"
            st.rerun()


def _refresh_all_stocks():
    """Refresh stock data for all tracked stocks."""
    for symbol in st.session_state.stock_conversations.keys():
        stock_data = get_stock_history(symbol, limit=30)
        st.session_state.stock_conversations[symbol]["stock_data"] = stock_data
    save_conversations()
