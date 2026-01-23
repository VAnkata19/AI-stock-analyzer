from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def extract_stock_symbol(text: str, llm_provider: Optional[str] = None, selected_model: Optional[str] = None) -> str | None:
    """Use AI to extract stock symbol from user text."""
    from providers import get_llm
    
    # Get the appropriate LLM based on provider
    try:
        import streamlit as st
        if llm_provider is None:
            llm_provider = st.session_state.get("llm_provider", "lm_studio")
        if selected_model is None:
            selected_model = st.session_state.get("selected_model", "")
    except:
        if llm_provider is None:
            llm_provider = "lm_studio"
        if selected_model is None:
            selected_model = ""
    
    llm = get_llm(llm_provider, selected_model)
    if llm is None:
        return None
    
    prompt = f"""Extract the stock ticker symbol from the following user question. 
If there is a stock symbol mentioned (like AAPL, NVDA, TSLA, etc.) or a company name (like Apple, Nvidia, Tesla), return ONLY the ticker symbol in uppercase.
If no stock symbol or company is mentioned, return "NONE".

Examples:
- "What's happening with Apple?" -> AAPL
- "Analyze NVDA" -> NVDA
- "Tell me about Nvidia" -> NVDA
- "How is Tesla doing?" -> TSLA

User question: {text}

Stock symbol:"""
    
    response = llm.invoke(prompt)
    content = response.content
    if isinstance(content, list):
        content = str(content[0]) if content else ""
    
    # Clean up the response - extract only alphabetic characters (the ticker)
    import re
    # Remove any special characters and extract potential ticker
    cleaned = re.sub(r'[^A-Za-z]', '', content.strip())
    symbol = cleaned.upper()
    
    # Validate the response
    if symbol == "NONE" or len(symbol) == 0 or len(symbol) > 5:
        return None
    
    return symbol
