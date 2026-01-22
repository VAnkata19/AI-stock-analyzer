import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import uuid


def display_chart(symbol: str, stock_data: dict, chart_key: str | None = None):
    """Display the stock chart.
    
    Args:
        symbol: The stock symbol.
        stock_data: The stock data dictionary.
        chart_key: Optional unique key for the chart element.
    """
    if "data" in stock_data and stock_data["data"]:
        # Convert to DataFrame
        df = pd.DataFrame(stock_data["data"])
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")
        
        st.subheader(f"📊 {symbol} Price Chart")
        
        # Create candlestick chart
        fig = go.Figure(data=[go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name=symbol
        )])
        
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            template="plotly_dark",
            height=350,
            margin=dict(l=0, r=0, t=30, b=0),
            xaxis_rangeslider_visible=False
        )
        
        # Use provided key or generate a unique one
        key = chart_key or f"chart_{uuid.uuid4()}"
        st.plotly_chart(fig, use_container_width=True, key=key)
        
        # Show latest price info
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        change = latest["close"] - prev["close"]
        change_pct = (change / prev["close"]) * 100
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Close", f"${latest['close']:.2f}", f"{change:+.2f} ({change_pct:+.2f}%)")
        m2.metric("Open", f"${latest['open']:.2f}")
        m3.metric("High", f"${latest['high']:.2f}")
        m4.metric("Low", f"${latest['low']:.2f}")
    else:
        st.error(f"Could not fetch data for {symbol}. Please check the symbol.")
