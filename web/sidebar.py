import streamlit as st
from stock import get_stock_logo_url, get_stock_history
from .state import clear_all_state
from history import save_conversations


def render_sidebar():
    """Render the sidebar with stock navigation."""
    with st.sidebar:
        st.markdown(
            '<h1 style="margin-top: -50px;">◈ Fintellix</h1>',
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
        
        st.divider()

        if st.button("+ New Chat", width="stretch"):
            st.session_state.selected_stock = None
            st.session_state.selected_view = "chat"
            st.rerun()
        
        if st.button("↻ Refresh All", width="stretch"):
            _refresh_all_stocks()
            st.rerun()
        
        if st.button("✕ Clear All", width="stretch"):
            clear_all_state()
            st.rerun()
        
        # Settings section at bottom
        with st.expander("Settings"):
            st.markdown("**LLM Provider**")
            
            # Provider selection dropdown
            providers = ["LM Studio", "Ollama", "OpenAI (ChatGPT)"]
            provider_keys = ["lm_studio", "ollama", "openai"]
            current_provider = st.session_state.get("llm_provider", "lm_studio")
            current_index = provider_keys.index(current_provider) if current_provider in provider_keys else 0
            
            selected_provider = st.selectbox(
                "Select Provider",
                providers,
                index=current_index,
                help="Choose your LLM provider"
            )
            provider_key = provider_keys[providers.index(selected_provider)]
            
            if provider_key != current_provider:
                st.session_state.llm_provider = provider_key
                st.session_state.selected_model = ""  # Reset model when provider changes
                from history import save_settings
                save_settings({"llm_provider": provider_key})
                st.rerun()
            
            # Model selection based on provider
            _render_model_selector(provider_key)

            
            # Beginner mode toggle (moved below LLM providers)
            beginner_mode = st.toggle(
                "Beginner Mode",
                value=st.session_state.beginner_mode,
                help="Shows simplified takeaways with ratings, risk levels, and advice for new investors"
            )
            if beginner_mode != st.session_state.beginner_mode:
                st.session_state.beginner_mode = beginner_mode
                # Save to persistent storage
                from history import save_settings
                save_settings({"beginner_mode": beginner_mode})
                st.rerun()


def _render_stock_item(symbol: str):
    """Render a single stock item in the sidebar."""
    # Check if analysis is running for this stock
    is_analyzing = symbol in st.session_state.active_threads
    analyzing_badge = " ..." if is_analyzing else ""
    
    # Check if this stock is currently selected
    is_selected = st.session_state.selected_stock == symbol
    button_type = "primary" if is_selected else "secondary"
    
    # Create button with logo
    if st.button(
        f"![logo]({get_stock_logo_url(symbol)}) {symbol}{analyzing_badge}",
        key=f"stock_btn_{symbol}",
        width="stretch",
        type=button_type
    ):
        st.session_state.selected_stock = symbol
        st.session_state.selected_view = "chat"
        st.rerun()


def _render_model_selector(provider_key: str):
    """Render the model selector based on the selected provider."""
    from reasoning.llm import get_lm_studio_models, get_ollama_models, get_openai_models
    from history import save_settings
    
    current_model = st.session_state.get("selected_model", "")
    
    if provider_key == "lm_studio":
        available_models = get_lm_studio_models()
        if available_models:
            if current_model not in available_models:
                current_model = available_models[0]
            
            selected_model = st.selectbox(
                "Model",
                available_models,
                index=available_models.index(current_model) if current_model in available_models else 0,
                help="Select a loaded model from LM Studio"
            )
            if selected_model != st.session_state.get("selected_model"):
                st.session_state.selected_model = selected_model
                save_settings({"selected_model": selected_model})
                st.rerun()
        else:
            st.warning("⚠️ No models loaded in LM Studio")
            st.caption("Make sure LM Studio is running and has a model loaded")
    
    elif provider_key == "ollama":
        available_models = get_ollama_models()
        if available_models:
            if current_model not in available_models:
                current_model = available_models[0]
            
            selected_model = st.selectbox(
                "Model",
                available_models,
                index=available_models.index(current_model) if current_model in available_models else 0,
                help="Select an Ollama model"
            )
            if selected_model != st.session_state.get("selected_model"):
                st.session_state.selected_model = selected_model
                save_settings({"selected_model": selected_model})
                st.rerun()
        else:
            st.warning("⚠️ No models found in Ollama")
            st.caption("Make sure Ollama is running on port 11434")
    
    elif provider_key == "openai":
        available_models = get_openai_models()
        if available_models:
            if current_model not in available_models:
                current_model = available_models[0]
            
            selected_model = st.selectbox(
                "Model",
                available_models,
                index=available_models.index(current_model) if current_model in available_models else 0,
                help="Select an OpenAI GPT model"
            )
            if selected_model != st.session_state.get("selected_model"):
                st.session_state.selected_model = selected_model
                save_settings({"selected_model": selected_model})
                st.rerun()
        else:
            st.warning("⚠️ No OpenAI models found")
            st.caption("Make sure OPENAI_API_KEY is set in your .env file")


def _refresh_all_stocks():
    """Refresh stock data for all tracked stocks."""
    for symbol in st.session_state.stock_conversations.keys():
        stock_data = get_stock_history(symbol, limit=30)
        st.session_state.stock_conversations[symbol]["stock_data"] = stock_data
    save_conversations()
