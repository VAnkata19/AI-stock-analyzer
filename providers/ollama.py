"""Ollama provider implementation."""

import os
from typing import List, Optional
from dotenv import load_dotenv

from .base import BaseLLMProvider

load_dotenv()


class OllamaProvider(BaseLLMProvider):
    """Ollama provider using LangChain."""
    
    name = "ollama"
    
    @property
    def base_url(self) -> str:
        return os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
    
    def get_models(self) -> List[str]:
        """Fetch available models from Ollama API."""
        import requests
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [model["name"] for model in models]
        except Exception as e:
            print(f"Error fetching Ollama models: {e}")
        return []
    
    def get_llm(self, model: Optional[str] = None):
        """Get a ChatOllama instance."""
        from langchain_ollama import ChatOllama
        return ChatOllama(
            model=model or "llama2",
            temperature=0,
            base_url=self.base_url
        )
    
    def run_agent(self, query: str, system_prompt: str, model: Optional[str] = None) -> str:
        """Run a query using LangChain agent with Ollama."""
        from langchain.agents import create_agent
        from langchain_core.messages import HumanMessage, SystemMessage
        from search import search_web
        from stock import get_stock_info
        from date_utils import get_current_date
        
        llm = self.get_llm(model)
        tools = [get_current_date, search_web, get_stock_info]
        agent = create_agent(model=llm, tools=tools)
        
        result = agent.invoke({
            "messages": [
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ]
        })
        return result["messages"][-1].content
    
    def is_available(self) -> bool:
        """Check if Ollama is running."""
        import requests
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
