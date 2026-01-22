"""Welcome page component - shown when no stock is selected."""

import streamlit as st
from stock import get_stock_history, extract_stock_symbol
from history import save_conversations


def render_new_chat_page():
    """Render the new chat page (no stock selected)."""
    
    # Welcome header
    st.markdown("## Welcome to AI Stock Analyzer")
    
    st.markdown("""
    Your personal AI-powered stock research assistant. Get real-time analysis, 
    charts, and insights for any stock in seconds.
    """)
    
    st.divider()
    
    # How to use section
    st.markdown("### Getting Started")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1. Ask about any stock**
        - Type a company name or ticker symbol
        - Example: *"Analyze Apple"* or *"How is TSLA doing?"*
        
        **2. View your analysis**
        - **Chart** - Interactive price chart
        - **Chat** - AI-generated analysis
        - **Competitors** - Compare against rivals
        """)
    
    with col2:
        st.markdown("""
        **3. What you'll get**
        - Today's price & daily performance
        - Recent news & market catalysts
        - Weekly/monthly trends
        - Long-term outlook & insights
        
        **4. Manage your stocks**
        - All analyzed stocks appear in the sidebar
        - Click to switch between stocks anytime
        """)
    
    # Process pending query for new stock
    if st.session_state.pending_query:
        _process_new_stock_query()
    
    # Chat input
    prompt = st.chat_input("Ask about any stock (e.g., 'Should I invest in Nvidia?' or 'Analyze Apple')")
    
    if prompt:
        st.session_state.pending_query = prompt
        st.rerun()


def _process_new_stock_query():
    """Process a query to detect and create a new stock conversation."""
    query = st.session_state.pending_query
    detected_symbol = extract_stock_symbol(query)
    
    if detected_symbol:
        # Create new conversation for this stock if it doesn't exist
        if detected_symbol not in st.session_state.stock_conversations:
            stock_data = get_stock_history(detected_symbol, limit=30)
            st.session_state.stock_conversations[detected_symbol] = {
                "messages": [{"role": "user", "content": query}],
                "stock_data": stock_data
            }
        else:
            st.session_state.stock_conversations[detected_symbol]["messages"].append({
                "role": "user",
                "content": query
            })
        
        # Save after creating/updating conversation
        save_conversations()
        
        # Switch to that stock
        st.session_state.selected_stock = detected_symbol
        st.rerun()
    else:
        st.session_state.pending_query = None
        st.warning("I couldn't detect a stock symbol in your question. Please mention a stock like 'NVDA', 'Apple', or 'Tesla'.")
