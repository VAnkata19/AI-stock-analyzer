"""Background task polling."""

import streamlit as st


@st.fragment(run_every=2)
def poll_background_tasks():
    """Poll for completed background tasks every 2 seconds."""
    if st.session_state.background_tasks:
        for symbol, future in list(st.session_state.background_tasks.items()):
            if future.done():
                st.rerun()
