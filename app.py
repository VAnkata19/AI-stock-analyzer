import streamlit as st
from dotenv import load_dotenv
from web import (
    setup_page_config,
    init_session_state,
    apply_custom_styles,
    render_sidebar,
    render_stock_page,
    render_new_chat_page,
    poll_background_tasks,
)

load_dotenv()

# Setup page config (must be first Streamlit command)
setup_page_config()

# Initialize session state
init_session_state()

# Apply custom styles
apply_custom_styles()

# Render sidebar
render_sidebar()

# Main content
if st.session_state.selected_stock:
    render_stock_page(st.session_state.selected_stock)
else:
    render_new_chat_page()

# Auto-refresh for background tasks
if st.session_state.active_threads:
    poll_background_tasks()

