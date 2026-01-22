import streamlit as st


def setup_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="AI Stock Analyzer",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
