import streamlit as st


SIDEBAR_CSS = """
<style>
    /* Hide the collapse button */
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    /* Hide expand button when collapsed */
    button[kind="headerNoPadding"] {
        display: none !important;
    }
    /* Force sidebar to always be visible and fixed width */
    [data-testid="stSidebar"] {
        min-width: 300px !important;
        max-width: 300px !important;
    }
    [data-testid="stSidebar"][aria-expanded="false"] {
        display: block !important;
        min-width: 300px !important;
        margin-left: 0 !important;
    }
    /* Hide any collapse arrow/chevron */
    [data-testid="stSidebar"] button[kind="header"] {
        display: none !important;
    }
    .st-emotion-cache-1gwvy71 {
        display: none !important;
    }
    /* Add top padding to main content area */
    [data-testid="stMain"] > div:first-child {
        padding-top: 50px !important;
    }
</style>
"""


def apply_custom_styles():
    """Apply custom CSS styles to the app."""
    st.markdown(SIDEBAR_CSS, unsafe_allow_html=True)
