"""Factory functions for LLM providers."""

from typing import Dict, List, Optional, Type, Any

from .base import BaseLLMProvider
from .lm_studio import LMStudioProvider
from .ollama import OllamaProvider
from .openai_provider import OpenAIProvider


# Registry of all available providers
PROVIDERS: Dict[str, Type[BaseLLMProvider]] = {
    "lm_studio": LMStudioProvider,
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
}


def get_provider(provider_name: Optional[str] = None) -> BaseLLMProvider:
    """Get a provider instance by name."""
    if provider_name is None:
        provider_name = "lm_studio"
    if provider_name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(PROVIDERS.keys())}")
    return PROVIDERS[provider_name]()


def get_llm(provider_name: Optional[str] = None, model: Optional[str] = None) -> Any:
    """Get an LLM instance for the given provider and model.
    
    Args:
        provider_name: LLM provider ('lm_studio', 'ollama', 'openai'). 
                      If None, reads from streamlit session.
        model: Model to use. If None, uses provider's default.
        
    Returns:
        LLM instance with invoke() method.
    """
    # Get provider from session state if not provided
    if provider_name is None:
        try:
            import streamlit as st
            provider_name = st.session_state.get("llm_provider", "lm_studio")
        except:
            provider_name = "lm_studio"
    
    if model is None:
        try:
            import streamlit as st
            model = st.session_state.get("selected_model", "")
        except:
            model = ""
    
    provider = get_provider(provider_name or "lm_studio")
    return provider.get_llm(model or None)


def get_available_models(provider_name: str) -> List[str]:
    """Get list of available models for a provider."""
    provider = get_provider(provider_name)
    return provider.get_models()


# Convenience functions for getting models from each provider
def get_lm_studio_models() -> List[str]:
    """Get available LM Studio models."""
    return LMStudioProvider().get_models()


def get_ollama_models() -> List[str]:
    """Get available Ollama models."""
    return OllamaProvider().get_models()


def get_openai_models() -> List[str]:
    """Get available OpenAI models."""
    return OpenAIProvider().get_models()
