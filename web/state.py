import streamlit as st
from concurrent.futures import ThreadPoolExecutor
from history import load_conversations, clear_conversations


def init_session_state():
    """Initialize all session state variables."""
    if "task_results" not in st.session_state:
        st.session_state.task_results = {}
    
    if "stock_conversations" not in st.session_state:
        # Load persisted conversations on first init
        st.session_state.stock_conversations = load_conversations()
    
    if "selected_stock" not in st.session_state:
        st.session_state.selected_stock = None
    
    if "selected_view" not in st.session_state:
        st.session_state.selected_view = "chat"  # "chart" or "chat"
    
    if "pending_query" not in st.session_state:
        st.session_state.pending_query = None
    
    if "background_tasks" not in st.session_state:
        st.session_state.background_tasks = {}  # {symbol: Future object}
    
    if "active_threads" not in st.session_state:
        st.session_state.active_threads = {}  # {symbol: True} - tracks which stocks have pending analysis
    
    if "executor" not in st.session_state:
        st.session_state.executor = ThreadPoolExecutor(max_workers=5)


def clear_all_state():
    """Clear all session state and persisted data."""
    st.session_state.stock_conversations = {}
    st.session_state.selected_stock = None
    st.session_state.selected_view = "chat"
    st.session_state.pending_query = None
    st.session_state.background_tasks = {}
    st.session_state.active_threads = {}
    # Remove the saved file
    clear_conversations()
