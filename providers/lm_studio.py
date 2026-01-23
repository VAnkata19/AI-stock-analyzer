"""LM Studio provider implementation."""

import os
import requests
from typing import List, Optional
from dotenv import load_dotenv

from .base import BaseLLMProvider

load_dotenv()


class LMStudioProvider(BaseLLMProvider):
    """LM Studio provider using LangChain ChatOpenAI with local OpenAI-compatible API."""
    
    name = "lm_studio"
    
    @property
    def base_url(self) -> str:
        return os.getenv("LM_STUDIO_BASE_URL", "http://127.0.0.1:1234/v1")
    
    def get_models(self) -> List[str]:
        """Fetch available models from LM Studio."""
        try:
            # First try native SDK
            from lmstudio import Client
            with Client() as client:
                models = client.llm.list_loaded()
                return [model.identifier for model in models]
        except:
            # Fallback to HTTP endpoint
            try:
                response = requests.get(f"{self.base_url}/models", timeout=2)
                if response.status_code == 200:
                    models = response.json().get("data", [])
                    return [m.get("id", "") for m in models if m.get("id")]
            except:
                pass
        return []
    
    def get_llm(self, model: Optional[str] = None):
        """Get a ChatOpenAI instance pointed at LM Studio."""
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            base_url=self.base_url,
            model=model or "local-model",
            temperature=0,
            api_key="lm-studio"  # Dummy key for local LM Studio
        )
    
    def run_agent(self, query: str, system_prompt: str, model: Optional[str] = None) -> str:
        """Run a query using LangChain agent with LM Studio."""
        from langchain.agents import create_agent
        from langchain_core.messages import HumanMessage, SystemMessage
        from search import search_web
        from stock import get_stock_info
        from date_utils import get_current_date
        
        try:
            llm = self.get_llm(model)
            tools = [get_current_date, search_web, get_stock_info]
            agent = create_agent(model=llm, tools=tools)
            
            result = agent.invoke({
                "messages": [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=query)
                ]
            })
            
            if "messages" in result and result["messages"]:
                return str(result["messages"][-1].content)
            else:
                return "No response generated"
                
        except Exception as e:
            print(f"Error during LM Studio agent: {e}", flush=True)
            import traceback
            traceback.print_exc()
            return f"Error: {str(e)}"



    
    @staticmethod
    def is_available() -> bool:
        """Check if LM Studio is running and accessible."""
        try:
            response = requests.get("http://127.0.0.1:1234/v1/models", timeout=2)
            return response.status_code == 200
        except:
            return False
