import streamlit as st
from stock import get_stock_logo_url, get_stock_history, extract_stock_symbol
from chart import display_chart
from history import save_conversations
from .tasks import run_analysis_task


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
    
    # View toggle tabs
    tab1, tab2 = st.tabs(["📊 Chart", "💬 Chat"])
    
    with tab1:
        _render_chart_tab(symbol, conv)
    
    with tab2:
        _render_chat_tab(symbol, conv)


def _render_chart_tab(symbol: str, conv: dict):
    """Render the chart tab for a stock."""
    if conv.get("stock_data"):
        display_chart(symbol, conv["stock_data"], chart_key=f"main_chart_{symbol}")
    else:
        st.info("No chart data available.")


def _render_chat_tab(symbol: str, conv: dict):
    """Render the chat tab for a stock."""
    # Check for completed background tasks for this stock
    _check_completed_tasks(symbol)
    
    # Display chat messages for this stock
    for i, msg in enumerate(conv.get("messages", [])):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Show spinner if analysis is running for this stock
    is_analyzing = symbol in st.session_state.active_threads
    if is_analyzing:
        with st.chat_message("assistant"):
            st.markdown("*Analyzing... (you can switch to other stocks while waiting)*")
    
    # Process pending query for this stock - start background thread
    _process_pending_query(symbol)
    
    # Chat input for this stock
    _render_chat_input(symbol, is_analyzing)


def _check_completed_tasks(symbol: str):
    """Check and process completed background tasks for a stock."""
    if symbol in st.session_state.background_tasks:
        future = st.session_state.background_tasks[symbol]
        if future.done():
            try:
                result = future.result()
                st.session_state.stock_conversations[symbol]["messages"].append({
                    "role": "assistant",
                    "content": result["response"]
                })
            except Exception as e:
                st.session_state.stock_conversations[symbol]["messages"].append({
                    "role": "assistant",
                    "content": f"Sorry, I encountered an error: {str(e)}"
                })
            # Save after adding assistant response
            save_conversations()
            # Clean up
            del st.session_state.background_tasks[symbol]
            if symbol in st.session_state.active_threads:
                del st.session_state.active_threads[symbol]
            st.rerun()


def _process_pending_query(symbol: str):
    """Process any pending query for a stock."""
    if st.session_state.pending_query and st.session_state.selected_stock == symbol:
        query = st.session_state.pending_query
        st.session_state.pending_query = None
        
        # Start background analysis using ThreadPoolExecutor
        future = st.session_state.executor.submit(run_analysis_task, symbol, query)
        st.session_state.background_tasks[symbol] = future
        st.session_state.active_threads[symbol] = True
        st.rerun()


def _render_chat_input(symbol: str, is_analyzing: bool):
    """Render the chat input for a stock. Only show if no user message has been sent yet."""
    conv = st.session_state.stock_conversations.get(symbol, {"messages": []})
    
    # Check if user has already sent a message for this stock
    has_user_message = any(msg["role"] == "user" for msg in conv.get("messages", []))
    
    # Don't show chat input if user already sent a message
    if has_user_message:
        return
    
    prompt = st.chat_input(f"Ask about {symbol}...")
    
    if prompt:
        st.session_state.stock_conversations[symbol]["messages"].append({
            "role": "user",
            "content": prompt
        })
        save_conversations()
        st.session_state.pending_query = prompt
        st.rerun()


def render_new_chat_page():
    """Render the new chat page (no stock selected)."""
    
    # Welcome header
    st.markdown("## 👋 Welcome to AI Stock Analyzer!")
    
    st.markdown("""
    Your personal AI-powered stock research assistant. Get real-time analysis, 
    charts, and insights for any stock in seconds.
    """)
    
    st.divider()
    
    # How to use section
    st.markdown("### 🚀 How to Get Started")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **1. Ask about any stock**
        - Type a company name or ticker symbol
        - Example: *"Analyze Apple"* or *"How is TSLA doing?"*
        
        **2. View your analysis**
        - 📊 **Chart** - Interactive price chart
        - 💬 **Chat** - AI-generated analysis
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
