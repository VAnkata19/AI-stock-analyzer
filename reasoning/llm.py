from dotenv import load_dotenv

load_dotenv()

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from search import search_web
from stock import get_stock_info
from date_utils import get_current_date

# System instructions for the AI agent
SYSTEM_PROMPT = """You are an expert stock market analyst AI assistant. Your job is to help users analyze stocks and make informed investment decisions.

You specialize in:
- Stock analysis and price movements
- Company financials and performance
- Market trends and industry news
- Investment strategies and stock comparisons
- Stock symbols, tickers, and market data
- Answering follow-up questions about stocks the user is currently discussing

IMPORTANT CONTEXT RULES:
- If the user's message mentions a specific stock OR if there is context about a stock they are asking about, ALWAYS treat it as a stock-related question.
- Follow-up questions like "should I invest?", "is it a good buy?", "what do you think?", "tell me more", etc. are ALWAYS stock-related when there is context about a stock.
- Only decline if the question is CLEARLY unrelated to stocks, investing, or financial markets (e.g., "what's the weather?", "tell me a joke").

If a question is clearly NOT about stocks or investing at all, politely say:
"I'm sorry, I can only help with stock-related questions. Please ask me about stocks, market analysis, or investment topics."

You have access to the following tools:
1. get_current_date - Use this FIRST to get today's date so you know the current date when searching for information.
2. search_web - Use this to search the internet for news, articles, and information about stocks, companies, and market trends.
3. get_stock_info - Use this to fetch the latest End of Day (EOD) stock price data for a given stock symbol.

When analyzing a stock, ALWAYS structure your response in this order:

1. **TODAY'S DAILY PERFORMANCE** (MOST IMPORTANT - Start with this):
   - First get the current date using get_current_date
   - Fetch the current stock price data using get_stock_info
   - Report today's price, daily change ($ and %), open/high/low/close
   - Compare to yesterday's close
   - Mention trading volume and if it's above/below average

2. **RECENT NEWS & CATALYSTS** (What happened today/this week):
   - Search for breaking news from today
   - Any earnings, announcements, or events affecting the stock
   - Analyst upgrades/downgrades

3. **WEEKLY/MONTHLY TREND**:
   - Price movement over the past week/month
   - Key support and resistance levels
   - Recent highs/lows

4. **BIG PICTURE OVERVIEW** (Only after daily context):
   - Company fundamentals and long-term outlook
   - Industry position and competitive landscape
   - Long-term investment thesis

5. **SUMMARY & OUTLOOK**:
   - Brief summary of daily action
   - Short-term vs long-term perspective
   - Always remind users that this is not financial advice"""

# Beginner takeaway section (added when beginner mode is on)
BEGINNER_SECTION = """

6. **🎯 BEGINNER TAKEAWAY** (ALWAYS include this section at the end):
   This is a simplified summary for beginners. Use these exact emoji formats:
   
   📈 **Overall Rating:** [Excellent / Good / Neutral / Poor / Avoid] + brief reason
   
   🟢 **Trend:** [Strong upward / Moderate upward / Sideways / Moderate downward / Strong downward] momentum
   
   ⚠️ **Risk Level:** [Low / Medium / Medium-High / High / Very High] + (brief explanation why)
   
   🕒 **Best For:** [Type of investor this stock suits, e.g., "Long-term investors who can handle volatility"]
   
   ❌ **Not Ideal For:** [Type of investor who should avoid, e.g., "Very cautious beginners or short-term traders"]
   
   💡 **Simple Advice:** One sentence of actionable advice for a beginner"""

# Set up the language model and tools
#---------------------------------------------------
llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
tools = [get_current_date, search_web, get_stock_info]
#---------------------------------------------------
# Create the agent
agent = create_agent(model=llm, tools=tools)
#---------------------------------------------------


# Runs the agent with a given query
def run_agent(query: str) -> str:
    """Run the agent with a given query.
    
    Args:
        query (str): The user's question or request.
        
    Returns:
        str: The agent's response (always includes beginner takeaway section).
    """
    # Always include beginner section - filtering happens at display time
    full_prompt = SYSTEM_PROMPT + BEGINNER_SECTION
    full_prompt += "\n\nBe concise, factual, and helpful. Cite your sources when providing information from web searches. Focus on actionable, timely information first."
    
    result = agent.invoke({
        "messages": [
            SystemMessage(content=full_prompt),
            HumanMessage(content=query)
        ]
    })
    return result["messages"][-1].content


def filter_response_for_mode(response: str, beginner_mode: bool) -> str:
    """Filter the response based on beginner mode setting.
    
    Args:
        response (str): The full agent response.
        beginner_mode (bool): Whether beginner mode is enabled.
        
    Returns:
        str: Filtered response - only beginner takeaway if beginner mode, 
             or full response without beginner section if not.
    """
    import re
    
    # Use regex to find beginner takeaway section - handles various formatting
    # Looks for the 🎯 emoji followed by BEGINNER (case insensitive)
    pattern = r'(?:^|\n)\s*(?:\d+\.\s*)?(?:\*+\s*)?(?:#+\s*)?🎯\s*\**\s*BEGINNER'
    match = re.search(pattern, response, re.IGNORECASE)
    
    if match:
        beginner_start = match.start()
        # Skip any leading newline
        if response[beginner_start] == '\n':
            beginner_start += 1
    else:
        beginner_start = -1
    
    if beginner_mode:
        # Only show beginner takeaway
        if beginner_start != -1:
            return response[beginner_start:]
        else:
            # Fallback if marker not found
            return response
    else:
        # Show full response without beginner takeaway
        if beginner_start != -1:
            return response[:beginner_start].rstrip()
        else:
            return response
