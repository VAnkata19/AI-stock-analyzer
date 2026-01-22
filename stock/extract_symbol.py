from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()


def extract_stock_symbol(text: str) -> str | None:
    """Use AI to extract stock symbol from user text."""
    llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)
    
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
    symbol = content.strip().upper()
    
    # Validate the response
    if symbol == "NONE" or len(symbol) > 5 or not symbol.isalpha():
        return None
    
    return symbol
