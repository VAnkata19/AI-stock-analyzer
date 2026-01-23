"""Chat tab component."""

import streamlit as st
from history import save_conversations
from reasoning import filter_response_for_mode
from ..tasks import run_analysis_task


def render_chat_tab(symbol: str, conv: dict):
    """Render the chat tab for a stock."""
    # Check for completed background tasks for this stock
    _check_completed_tasks(symbol)
    
    # Get current beginner mode setting
    beginner_mode = st.session_state.get("beginner_mode", True)
    
    # Display chat messages for this stock
    for i, msg in enumerate(conv.get("messages", [])):
        with st.chat_message(msg["role"]):
            # Filter assistant responses based on beginner mode
            if msg["role"] == "assistant":
                filtered_content = filter_response_for_mode(msg["content"], beginner_mode)
                st.markdown(filtered_content)
            else:
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
        
        # Get current provider and model from session state
        llm_provider = st.session_state.get("llm_provider", "lm_studio")
        selected_model = st.session_state.get("selected_model", "")
        
        # Start background analysis using ThreadPoolExecutor
        future = st.session_state.executor.submit(
            run_analysis_task, 
            symbol, 
            query,
            llm_provider=llm_provider,
            selected_model=selected_model
        )
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
