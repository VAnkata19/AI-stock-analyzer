"""OpenAI provider implementation."""

import os
from typing import List, Optional

from .base import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI provider using LangChain."""
    
    name = "openai"
    
    def get_models(self) -> List[str]:
        """Fetch available GPT models from OpenAI API."""
        try:
            import openai
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return []
            
            client = openai.OpenAI(api_key=api_key)
            models = client.models.list()
            
            # Filter for GPT models that are commonly used for chat
            gpt_models = [
                m.id for m in models 
                if "gpt" in m.id.lower() 
                and not any(x in m.id for x in ["realtime", "audio", "tts", "instruct", "image"])
            ]
            
            # Sort with most capable models first, including GPT-3.5
            priority = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo", "gpt-3"]
            sorted_models = []
            for p in priority:
                for m in gpt_models:
                    if m.startswith(p) and m not in sorted_models:
                        sorted_models.append(m)
            # Add remaining models
            for m in gpt_models:
                if m not in sorted_models:
                    sorted_models.append(m)
            
            return sorted_models[:20]  # Limit to 20 models (increased from 15 to include more GPT-3.5 variants)
        except Exception as e:
            print(f"Error fetching OpenAI models: {e}")
        return []
    
    def get_llm(self, model: Optional[str] = None):
        """Get a ChatOpenAI instance."""
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model or "gpt-4-turbo",
            temperature=0
        )
    
    def run_agent(self, query: str, system_prompt: str, model: Optional[str] = None) -> str:
        """Run a query using LangChain agent with OpenAI."""
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
    
    @staticmethod
    def is_available() -> bool:
        """Check if OpenAI API key is set."""
        return bool(os.getenv("OPENAI_API_KEY"))
