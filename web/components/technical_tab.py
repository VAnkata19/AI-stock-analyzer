"""Technical Analysis tab component."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from stock import get_stock_history


def render_technical_tab(symbol: str, conv: dict):
    """Render the technical analysis tab for a stock."""
    # Get more data for technical analysis
    stock_data = get_stock_history(symbol, limit=100)
    
    if not stock_data or "data" not in stock_data or not stock_data["data"]:
        st.warning("Unable to fetch stock data for technical analysis.")
        return
    
    df = pd.DataFrame(stock_data["data"])
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    
    # Calculate technical indicators
    df = _calculate_indicators(df)
    
    # Display current signals
    _render_signal_summary(df, symbol)
    
    st.divider()
    
    # Chart with indicators
    _render_technical_chart(df, symbol)
    
    st.divider()
    
    # Indicator details
    _render_indicator_details(df)


def _calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate technical indicators."""
    # Moving Averages
    df["SMA_20"] = df["close"].rolling(window=20).mean()
    df["SMA_50"] = df["close"].rolling(window=50).mean()
    df["EMA_12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["EMA_26"] = df["close"].ewm(span=26, adjust=False).mean()
    
    # MACD
    df["MACD"] = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"] = df["MACD"] - df["MACD_Signal"]
    
    # RSI (14-period)
    delta = df["close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands
    df["BB_Middle"] = df["close"].rolling(window=20).mean()
    bb_std = df["close"].rolling(window=20).std()
    df["BB_Upper"] = df["BB_Middle"] + (bb_std * 2)
    df["BB_Lower"] = df["BB_Middle"] - (bb_std * 2)
    
    # Volume SMA
    df["Volume_SMA"] = df["volume"].rolling(window=20).mean()
    
    return df


def _render_signal_summary(df: pd.DataFrame, symbol: str):
    """Render a summary of current signals."""
    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else latest
    
    st.markdown(f"### Signal Summary — {symbol}")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # RSI Signal
    with col1:
        rsi = latest["RSI"]
        if pd.notna(rsi):
            if rsi > 70:
                signal, color, icon = "Overbought", "#ff5252", "🔴"
            elif rsi < 30:
                signal, color, icon = "Oversold", "#00c853", "🟢"
            else:
                signal, color, icon = "Neutral", "#ffc107", "🟡"
            st.metric("RSI (14)", f"{rsi:.1f}", signal)
        else:
            st.metric("RSI (14)", "N/A", "Insufficient data")
    
    # MACD Signal
    with col2:
        macd = latest["MACD"]
        macd_signal = latest["MACD_Signal"]
        if pd.notna(macd) and pd.notna(macd_signal):
            if macd > macd_signal:
                signal, delta = "Bullish", "↑ Above Signal"
            else:
                signal, delta = "Bearish", "↓ Below Signal"
            st.metric("MACD", f"{macd:.2f}", delta)
        else:
            st.metric("MACD", "N/A", "Insufficient data")
    
    # Moving Average Signal
    with col3:
        sma20 = latest["SMA_20"]
        sma50 = latest["SMA_50"]
        price = latest["close"]
        if pd.notna(sma20) and pd.notna(sma50):
            if price > sma20 > sma50:
                signal = "Strong Bullish"
            elif price > sma20:
                signal = "Bullish"
            elif price < sma20 < sma50:
                signal = "Strong Bearish"
            else:
                signal = "Bearish"
            st.metric("Trend (SMA)", signal, f"Price vs SMA20: {((price/sma20)-1)*100:+.1f}%")
        else:
            st.metric("Trend (SMA)", "N/A", "Insufficient data")
    
    # Bollinger Band Position
    with col4:
        bb_upper = latest["BB_Upper"]
        bb_lower = latest["BB_Lower"]
        price = latest["close"]
        if pd.notna(bb_upper) and pd.notna(bb_lower):
            bb_range = bb_upper - bb_lower
            bb_position = (price - bb_lower) / bb_range * 100
            if bb_position > 80:
                signal = "Near Upper Band"
            elif bb_position < 20:
                signal = "Near Lower Band"
            else:
                signal = "Mid Range"
            st.metric("Bollinger %", f"{bb_position:.0f}%", signal)
        else:
            st.metric("Bollinger %", "N/A", "Insufficient data")


def _render_technical_chart(df: pd.DataFrame, symbol: str):
    """Render the technical analysis chart with indicators."""
    # Create subplot with 3 rows
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=(f"{symbol} Price with Indicators", "MACD", "RSI")
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df["date"],
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            name="Price"
        ),
        row=1, col=1
    )
    
    # Bollinger Bands
    fig.add_trace(
        go.Scatter(x=df["date"], y=df["BB_Upper"], name="BB Upper",
                   line=dict(color="rgba(173, 216, 230, 0.5)", width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df["date"], y=df["BB_Lower"], name="BB Lower",
                   line=dict(color="rgba(173, 216, 230, 0.5)", width=1),
                   fill='tonexty', fillcolor='rgba(173, 216, 230, 0.1)'),
        row=1, col=1
    )
    
    # Moving Averages
    fig.add_trace(
        go.Scatter(x=df["date"], y=df["SMA_20"], name="SMA 20",
                   line=dict(color="#ffc107", width=1.5)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df["date"], y=df["SMA_50"], name="SMA 50",
                   line=dict(color="#2196f3", width=1.5)),
        row=1, col=1
    )
    
    # MACD
    colors = ['#00c853' if val >= 0 else '#ff5252' for val in df["MACD_Hist"]]
    fig.add_trace(
        go.Bar(x=df["date"], y=df["MACD_Hist"], name="MACD Histogram",
               marker_color=colors),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df["date"], y=df["MACD"], name="MACD",
                   line=dict(color="#2196f3", width=1.5)),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=df["date"], y=df["MACD_Signal"], name="Signal",
                   line=dict(color="#ff9800", width=1.5)),
        row=2, col=1
    )
    
    # RSI
    fig.add_trace(
        go.Scatter(x=df["date"], y=df["RSI"], name="RSI",
                   line=dict(color="#9c27b0", width=1.5)),
        row=3, col=1
    )
    # Overbought/Oversold lines - add shapes directly to RSI subplot
    fig.add_shape(type="line", y0=70, y1=70, x0=0, x1=1, xref="x3 domain", yref="y3",
                  line=dict(color="red", dash="dash"))
    fig.add_shape(type="line", y0=30, y1=30, x0=0, x1=1, xref="x3 domain", yref="y3",
                  line=dict(color="green", dash="dash"))
    fig.add_shape(type="rect", y0=70, y1=100, x0=0, x1=1, xref="x3 domain", yref="y3",
                  fillcolor="red", opacity=0.1, line_width=0)
    fig.add_shape(type="rect", y0=0, y1=30, x0=0, x1=1, xref="x3 domain", yref="y3",
                  fillcolor="green", opacity=0.1, line_width=0)
    
    # Update layout
    fig.update_layout(
        template="plotly_dark",
        height=700,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis_rangeslider_visible=False,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    fig.update_yaxes(title_text="Price ($)", row=1, col=1)
    fig.update_yaxes(title_text="MACD", row=2, col=1)
    fig.update_yaxes(title_text="RSI", row=3, col=1, range=[0, 100])
    
    st.plotly_chart(fig, width="stretch")


def _render_indicator_details(df: pd.DataFrame):
    """Render detailed indicator explanations."""
    latest = df.iloc[-1]
    
    st.markdown("### Indicator Guide")
    
    with st.expander("Moving Averages (SMA 20 & 50)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Simple Moving Average (SMA)** smooths price data over a period.
            - **SMA 20** (yellow): Short-term trend
            - **SMA 50** (blue): Medium-term trend
            """)
        with col2:
            if pd.notna(latest["SMA_20"]) and pd.notna(latest["SMA_50"]):
                st.markdown(f"""
                **Current Values:**
                - SMA 20: **${latest['SMA_20']:.2f}**
                - SMA 50: **${latest['SMA_50']:.2f}**
                - Price vs SMA 20: **{((latest['close']/latest['SMA_20'])-1)*100:+.2f}%**
                """)
    
    with st.expander("RSI (Relative Strength Index)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **RSI** measures momentum on a scale of 0-100.
            - **Above 70**: Overbought (potential sell signal)
            - **Below 30**: Oversold (potential buy signal)
            - **50**: Neutral
            """)
        with col2:
            if pd.notna(latest["RSI"]):
                rsi = latest["RSI"]
                status = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Neutral"
                st.markdown(f"""
                **Current Value:** **{rsi:.1f}**
                
                Status: **{status}**
                """)
    
    with st.expander("MACD (Moving Average Convergence Divergence)", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **MACD** shows relationship between two EMAs.
            - **MACD Line**: EMA(12) - EMA(26)
            - **Signal Line**: 9-day EMA of MACD
            - **Histogram**: MACD - Signal
            
            **Signals:**
            - MACD crosses above Signal = Bullish
            - MACD crosses below Signal = Bearish
            """)
        with col2:
            if pd.notna(latest["MACD"]) and pd.notna(latest["MACD_Signal"]):
                signal = "Bullish" if latest["MACD"] > latest["MACD_Signal"] else "Bearish"
                st.markdown(f"""
                **Current Values:**
                - MACD: **{latest['MACD']:.3f}**
                - Signal: **{latest['MACD_Signal']:.3f}**
                - Histogram: **{latest['MACD_Hist']:.3f}**
                
                Signal: **{signal}**
                """)
    
    with st.expander("Bollinger Bands", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Bollinger Bands** show volatility and potential price levels.
            - **Middle Band**: 20-day SMA
            - **Upper Band**: Middle + 2 std deviations
            - **Lower Band**: Middle - 2 std deviations
            
            **Signals:**
            - Price near upper band = potentially overbought
            - Price near lower band = potentially oversold
            - Bands narrowing = low volatility, breakout possible
            """)
        with col2:
            if pd.notna(latest["BB_Upper"]) and pd.notna(latest["BB_Lower"]):
                bb_width = ((latest["BB_Upper"] - latest["BB_Lower"]) / latest["BB_Middle"]) * 100
                st.markdown(f"""
                **Current Values:**
                - Upper: **${latest['BB_Upper']:.2f}**
                - Middle: **${latest['BB_Middle']:.2f}**
                - Lower: **${latest['BB_Lower']:.2f}**
                - Band Width: **{bb_width:.1f}%**
                """)
