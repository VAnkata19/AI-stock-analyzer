import os

import requests
from dotenv import load_dotenv
from langchain.tools import tool

load_dotenv()


def get_stock_history(symbol: str, limit: int = 30) -> dict:
    """Fetches historical EOD data for charting.
    Args:
        symbol (str): The stock symbol to fetch information for.
        limit (int): Number of days of history to fetch.
    Returns: 
        dict: The stock historical data.
    """
    API_KEY = os.getenv("MARKETSTACK_API_KEY")
    BASE_URL = "http://api.marketstack.com/v1/eod"

    params = {
        "access_key": API_KEY,
        "symbols": symbol,
        "limit": limit,
        "sort": "DESC"
    }

    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data


@tool
def get_stock_info(symbol: str) -> dict:
    """Fetches the EOD (End of Day) information for stock from MarketStack API.
    Args:
        symbol (str): The stock symbol to fetch information for.
    Returns: 
        dict: The stock information.
    """

    API_KEY = os.getenv("MARKETSTACK_API_KEY")
    BASE_URL = "http://api.marketstack.com/v1/eod"

    params = {
        "access_key": API_KEY,
        "symbols": symbol,
        "limit": 1,
        "sort": "DESC"
    }

    print(f"Getting stock info for: '{symbol}'")
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    return data
