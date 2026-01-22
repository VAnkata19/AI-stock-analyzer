"""Competitor analysis task."""

from reasoning import run_agent


def run_competitor_analysis_task(symbol: str, competitors: list[str]) -> dict:
    """Run AI competitor comparison analysis. Designed to run in background thread."""
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
        
        response = run_agent(query)
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
