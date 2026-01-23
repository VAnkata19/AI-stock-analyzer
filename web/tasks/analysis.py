"""Stock analysis task."""

from reasoning import run_agent


def run_analysis_task(symbol: str, query: str, llm_provider: str = None, selected_model: str = None) -> dict:
    """Run AI analysis and return result dict. Designed to run in background thread.
    
    Args:
        symbol (str): Stock symbol being analyzed
        query (str): User's query
        llm_provider (str): LLM provider to use (from streamlit session)
        selected_model (str): Model to use (from streamlit session)
    """
    try:
        context = f"The user is asking about {symbol}. "
        full_query = context + query
        response = run_agent(full_query, llm_provider=llm_provider, selected_model=selected_model)
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
