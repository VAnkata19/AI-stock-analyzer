"""Base class for LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Optional, Any


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    name: str = "base"
    
    @abstractmethod
    def get_models(self) -> List[str]:
        """Get list of available models from this provider."""
        pass
    
    @abstractmethod
    def get_llm(self, model: Optional[str] = None) -> Any:
        """Get an LLM instance for simple invoke() calls."""
        pass
    
    @abstractmethod
    def run_agent(self, query: str, system_prompt: str, model: Optional[str] = None) -> str:
        """Run an agent query with the given system prompt."""
        pass
    
    @staticmethod
    def is_available() -> bool:
        """Check if this provider is available (service running, API key set, etc.)."""
        return False
