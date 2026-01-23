"""Competitor analysis task."""

from providers import get_provider

# Simplified system prompt for competitor analysis (no decline message)
COMPETITOR_SYSTEM_PROMPT = """You are an expert stock market analyst. Your job is to compare stocks and provide investment analysis.

You have access to these tools:
1. get_current_date - Get today's date
2. search_web - Search for news and information about stocks
3. get_stock_info - Get stock price data

Always use the tools to get current data before making comparisons. Be concise and actionable."""


def run_competitor_analysis_task(symbol: str, competitors: list[str], llm_provider: str = None, selected_model: str = None) -> dict:
    """Run AI competitor comparison analysis. Designed to run in background thread.
    
    Args:
        symbol (str): Stock symbol being analyzed
        competitors (list[str]): List of competitor symbols
        llm_provider (str): LLM provider to use (from streamlit session)
        selected_model (str): Model to use (from streamlit session)
    """
    try:
        comp_list = ", ".join(competitors)
        query = f"""Compare {symbol} against its main competitors: {comp_list}.

Provide a competitive analysis covering:

1. **PERFORMANCE COMPARISON** (Last 30 days):
   - Which stock performed best/worst recently?
   - Price changes and momentum comparison

2. **MARKET POSITION**:
   - Market cap comparison
   - Industry leadership ranking
   - Recent news/catalysts for each

3. **INVESTMENT COMPARISON**:
   - Which is the better value right now?
   - Risk comparison between them
   - Growth potential ranking

4. **VERDICT**:
   - Rank these stocks from best to worst for investment today
   - Explain your ranking briefly

Keep the analysis concise and actionable. Focus on what matters for making an investment decision TODAY."""
        
        # Use the provider directly with a simpler system prompt
        provider = get_provider(llm_provider or "lm_studio")
        response = provider.run_agent(query, COMPETITOR_SYSTEM_PROMPT, selected_model or None)
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
