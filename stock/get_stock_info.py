import yfinance as yf
from langchain.tools import tool


def get_stock_history(symbol: str, limit: int = 30) -> dict:
    """Fetches historical EOD data for charting using Yahoo Finance.
    Args:
        symbol (str): The stock symbol to fetch information for.
        limit (int): Number of days of history to fetch.
    Returns: 
        dict: The stock historical data.
    """
    try:
        ticker = yf.Ticker(symbol)
        # Get historical data (limit days + buffer for weekends/holidays)
        hist = ticker.history(period=f"{limit + 15}d")
        
        if hist.empty:
            return {"error": f"No data found for {symbol}"}
        
        # Take only the requested number of trading days
        hist = hist.tail(limit)
        
        # Convert to the format expected by the app
        data = []
        for idx, row in hist.iterrows():
            data.append({
                "date": idx.strftime("%Y-%m-%dT%H:%M:%S+0000"),  # type: ignore
                "symbol": symbol,
                "open": float(round(row["Open"], 4)),
                "high": float(round(row["High"], 4)),
                "low": float(round(row["Low"], 4)),
                "close": float(round(row["Close"], 4)),
                "volume": int(row["Volume"])
            })
        
        # Return in descending order (newest first)
        data.reverse()
        return {"data": data}
    except Exception as e:
        return {"error": str(e)}


@tool
def get_stock_info(symbol: str) -> dict:
    """Fetches the latest stock information using Yahoo Finance.
    Args:
        symbol (str): The stock symbol to fetch information for.
    Returns: 
        dict: The stock information including price, change, and basic stats.
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="5d")
        
        if hist.empty:
            return {"error": f"No data found for {symbol}"}
        
        # Get latest data
        latest = hist.iloc[-1]
        prev_close = hist.iloc[-2]["Close"] if len(hist) > 1 else latest["Close"]
        
        info = ticker.info
        
        print(f"Getting stock info for: '{symbol}'")
        
        return {
            "data": [{
                "symbol": symbol,
                "date": hist.index[-1].strftime("%Y-%m-%dT%H:%M:%S+0000"),
                "open": round(latest["Open"], 4),
                "high": round(latest["High"], 4),
                "low": round(latest["Low"], 4),
                "close": round(latest["Close"], 4),
                "volume": int(latest["Volume"]),
                "prev_close": round(prev_close, 4),
                "change": round(latest["Close"] - prev_close, 4),
                "change_percent": round((latest["Close"] - prev_close) / prev_close * 100, 2),
                "name": info.get("shortName", symbol),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow")
            }]
        }
    except Exception as e:
        return {"error": str(e)}
