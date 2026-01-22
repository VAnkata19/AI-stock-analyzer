import streamlit as st
from reasoning import run_agent


def run_analysis_task(symbol: str, query: str) -> dict:
    """Run AI analysis and return result dict. Designed to run in background thread."""
    try:
        context = f"The user is asking about {symbol}. "
        full_query = context + query
        response = run_agent(full_query)
        return {
            "status": "complete",
            "response": response,
            "symbol": symbol
        }
    except Exception as e:
        return {
            "status": "error",
            "response": f"Sorry, I encountered an error: {str(e)}",
            "symbol": symbol
        }


@st.fragment(run_every=2)
def poll_background_tasks():
    """Poll for completed background tasks every 2 seconds."""
    if st.session_state.background_tasks:
        for symbol, future in list(st.session_state.background_tasks.items()):
            if future.done():
                st.rerun()
