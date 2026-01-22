"""Stock competitor mappings and comparison utilities."""

# Common stock competitors by sector/industry
COMPETITORS = {
    # Tech Giants
    "AAPL": ["MSFT", "GOOGL", "AMZN", "META"],
    "MSFT": ["AAPL", "GOOGL", "AMZN", "ORCL"],
    "GOOGL": ["META", "MSFT", "AMZN", "AAPL"],
    "AMZN": ["MSFT", "GOOGL", "WMT", "SHOP"],
    "META": ["GOOGL", "SNAP", "PINS", "TWTR"],
    
    # EV & Auto
    "TSLA": ["RIVN", "F", "GM", "NIO"],
    "RIVN": ["TSLA", "LCID", "F", "GM"],
    "F": ["GM", "TSLA", "TM", "STLA"],
    "GM": ["F", "TSLA", "TM", "STLA"],
    "NIO": ["TSLA", "XPEV", "LI", "RIVN"],
    
    # Semiconductors
    "NVDA": ["AMD", "INTC", "QCOM", "AVGO"],
    "AMD": ["NVDA", "INTC", "QCOM", "MU"],
    "INTC": ["AMD", "NVDA", "QCOM", "TXN"],
    
    # Finance
    "JPM": ["BAC", "WFC", "GS", "MS"],
    "BAC": ["JPM", "WFC", "C", "USB"],
    "GS": ["MS", "JPM", "BAC", "SCHW"],
    
    # Retail
    "WMT": ["TGT", "COST", "AMZN", "KR"],
    "TGT": ["WMT", "COST", "KR", "DG"],
    "COST": ["WMT", "TGT", "BJ", "KR"],
    
    # Streaming/Entertainment
    "NFLX": ["DIS", "WBD", "PARA", "AMZN"],
    "DIS": ["NFLX", "WBD", "PARA", "CMCSA"],
    
    # Airlines
    "DAL": ["UAL", "AAL", "LUV", "JBLU"],
    "UAL": ["DAL", "AAL", "LUV", "ALK"],
    "AAL": ["DAL", "UAL", "LUV", "JBLU"],
    
    # Pharma/Biotech
    "PFE": ["JNJ", "MRK", "ABBV", "LLY"],
    "JNJ": ["PFE", "MRK", "ABBV", "BMY"],
    "MRNA": ["PFE", "BNTX", "NVAX", "JNJ"],
    
    # Energy
    "XOM": ["CVX", "COP", "BP", "SHEL"],
    "CVX": ["XOM", "COP", "BP", "SHEL"],
    
    # Fast Food
    "MCD": ["YUM", "SBUX", "CMG", "DPZ"],
    "SBUX": ["MCD", "DNKN", "CMG", "YUM"],
    
    # Social/Tech
    "SNAP": ["META", "PINS", "TWTR"],
    "PINS": ["META", "SNAP", "ETSY"],
    
    # E-commerce
    "SHOP": ["SQ", "AMZN", "EBAY", "ETSY"],
    "EBAY": ["AMZN", "ETSY", "SHOP", "MELI"],
    
    # Cloud/SaaS
    "CRM": ["MSFT", "ORCL", "SAP", "NOW"],
    "ORCL": ["CRM", "MSFT", "SAP", "IBM"],
    
    # Payment
    "V": ["MA", "PYPL", "SQ", "AXP"],
    "MA": ["V", "PYPL", "AXP", "DFS"],
    "PYPL": ["SQ", "V", "MA", "AFRM"],
}

# Sector mappings for fallback
SECTOR_PEERS = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "META", "NVDA"],
    "Consumer Cyclical": ["AMZN", "TSLA", "HD", "NKE", "MCD"],
    "Healthcare": ["JNJ", "UNH", "PFE", "MRK", "ABBV"],
    "Financial Services": ["JPM", "BAC", "WFC", "GS", "V"],
    "Communication Services": ["GOOGL", "META", "NFLX", "DIS", "VZ"],
    "Energy": ["XOM", "CVX", "COP", "SLB", "EOG"],
    "Industrials": ["CAT", "BA", "UNP", "HON", "GE"],
}


def get_competitors(symbol: str, limit: int = 4) -> list[str]:
    """Get list of competitors for a given stock symbol.
    
    Args:
        symbol: Stock ticker symbol
        limit: Maximum number of competitors to return
        
    Returns:
        List of competitor ticker symbols
    """
    symbol = symbol.upper()
    
    if symbol in COMPETITORS:
        return COMPETITORS[symbol][:limit]
    
    # Return empty if no competitors found
    return []


def get_all_for_comparison(symbol: str) -> list[str]:
    """Get the symbol plus its competitors for comparison.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        List with the symbol first, followed by competitors
    """
    competitors = get_competitors(symbol)
    return [symbol] + competitors
