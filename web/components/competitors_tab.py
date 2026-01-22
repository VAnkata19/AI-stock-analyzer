"""Competitors tab component."""

import streamlit as st
from stock import get_stock_logo_url, get_competitors, get_stock_history
from reasoning import filter_response_for_mode
from history import save_conversations
from ..tasks import run_competitor_analysis_task, run_analysis_task


def render_competitors_tab(symbol: str):
    """Render the competitors comparison tab for a stock."""
    competitors = get_competitors(symbol)
    
    if not competitors:
        st.info(f"No competitor data available for {symbol}. Try a major stock like AAPL, TSLA, NVDA, etc.")
        return
    
    # Add CSS to center popovers
    st.markdown("""
    <style>
    /* Center the popover button */
    div[data-testid="stPopover"] {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show competitor logos with popovers containing chart and button
    st.markdown("**Comparing against:** *(click symbol for details)*")
    
    cols = st.columns(len(competitors))
    for i, comp in enumerate(competitors):
        with cols[i]:
            _render_competitor_hover_card(comp, symbol)
    
    st.divider()
    
    # Check for competitor analysis key
    comp_key = f"competitor_analysis_{symbol}"
    
    # Get saved competitor analysis from conversation (persisted)
    conv = st.session_state.stock_conversations.get(symbol, {})
    saved_analysis = conv.get("competitor_analysis")
    
    # Check for completed background tasks for competitor analysis
    if comp_key in st.session_state.background_tasks:
        future = st.session_state.background_tasks[comp_key]
        if future.done():
            try:
                result = future.result()
                # Save to conversation for persistence
                st.session_state.stock_conversations[symbol]["competitor_analysis"] = result["response"]
                save_conversations()
            except Exception as e:
                st.session_state.stock_conversations[symbol]["competitor_analysis"] = f"Error: {str(e)}"
                save_conversations()
            del st.session_state.background_tasks[comp_key]
            if comp_key in st.session_state.active_threads:
                del st.session_state.active_threads[comp_key]
            st.rerun()
    
    # Show analysis or auto-start if not running
    if saved_analysis:
        # Get beginner mode setting
        beginner_mode = st.session_state.get("beginner_mode", True)
        filtered = filter_response_for_mode(saved_analysis, beginner_mode)
        st.markdown(filtered)
        
        # Refresh button
        if st.button("↻ Refresh Analysis", key=f"refresh_comp_{symbol}"):
            st.session_state.stock_conversations[symbol]["competitor_analysis"] = None
            # Clear the started tracking so it can run again
            if "competitor_analysis_started" in st.session_state:
                st.session_state.competitor_analysis_started.discard(comp_key)
            save_conversations()
            st.rerun()
    elif comp_key in st.session_state.active_threads:
        st.markdown("*Analyzing competitors... this may take a moment*")
    elif comp_key not in st.session_state.get("competitor_analysis_started", set()):
        # Track that we've started analysis for this symbol to prevent re-triggering
        if "competitor_analysis_started" not in st.session_state:
            st.session_state.competitor_analysis_started = set()
        st.session_state.competitor_analysis_started.add(comp_key)
        
        # Auto-start competitor analysis
        future = st.session_state.executor.submit(
            run_competitor_analysis_task, symbol, competitors
        )
        st.session_state.background_tasks[comp_key] = future
        st.session_state.active_threads[comp_key] = True
        st.markdown("*Analyzing competitors... this may take a moment*")
        st.rerun()
    else:
        # Analysis was started but not in active_threads - might be a stale state
        st.markdown("*Analyzing competitors... this may take a moment*")


def _render_competitor_hover_card(comp: str, current_symbol: str):
    """Render a competitor with popover showing chart and add button."""
    import plotly.graph_objects as go
    import pandas as pd
    
    # Always fetch fresh stock data for chart
    stock_data = get_stock_history(comp, limit=30)
    
    # Center container for logo and popover
    st.markdown(
        f'<div style="display: flex; flex-direction: column; align-items: center;">'
        f'<img src="{get_stock_logo_url(comp)}" width="60" style="border-radius: 8px; margin-bottom: 8px;">'
        f'</div>',
        unsafe_allow_html=True
    )
    
    # Center the popover using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.popover(comp, use_container_width=True):
            # Header with logo
            st.markdown(
                f'<div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">'
                f'<img src="{get_stock_logo_url(comp)}" width="40" style="border-radius: 6px;">'
                f'<strong style="font-size: 20px;">{comp}</strong>'
                f'</div>',
                unsafe_allow_html=True
            )
            
            # Show price info
            if stock_data and "data" in stock_data and len(stock_data["data"]) >= 2:
                latest = stock_data["data"][0]
                prev = stock_data["data"][1]
                price = latest.get("close", 0)
                change = price - prev.get("close", price)
                change_pct = (change / prev.get("close", 1)) * 100 if prev.get("close") else 0
                color = "#00c853" if change >= 0 else "#ff5252"
                sign = "+" if change >= 0 else ""
                st.markdown(
                    f'<div style="margin-bottom: 10px;">'
                    f'<span style="font-size: 20px; font-weight: bold;">${price:.2f}</span> '
                    f'<span style="color: {color};">{sign}{change:.2f} ({sign}{change_pct:.1f}%)</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
            
            # Display mini chart
            if stock_data and "data" in stock_data and stock_data["data"]:
                df = pd.DataFrame(stock_data["data"])
                df["date"] = pd.to_datetime(df["date"])
                df = df.sort_values("date")
                
                # Create simple line chart for popover
                fig = go.Figure(data=[go.Scatter(
                    x=df["date"],
                    y=df["close"],
                    mode='lines',
                    line=dict(color='#00c853' if df["close"].iloc[-1] >= df["close"].iloc[0] else '#ff5252', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(0, 200, 83, 0.1)' if df["close"].iloc[-1] >= df["close"].iloc[0] else 'rgba(255, 82, 82, 0.1)'
                )])
                
                fig.update_layout(
                    template="plotly_dark",
                    height=150,
                    margin=dict(l=0, r=0, t=10, b=0),
                    xaxis=dict(showticklabels=False, showgrid=False),
                    yaxis=dict(showticklabels=False, showgrid=False),
                    showlegend=False
                )
                
                st.plotly_chart(fig, key=f"mini_chart_{comp}_{current_symbol}", use_container_width=True)
            else:
                st.caption("Chart data unavailable")
            
            # Add/View button inside popover
            already_tracked = comp in st.session_state.stock_conversations
            
            if already_tracked:
                if st.button(f"View {comp}", key=f"view_{comp}_{current_symbol}", width="stretch"):
                    st.session_state.selected_stock = comp
                    st.session_state.selected_view = "chat"
                    st.rerun()
            else:
                if st.button(f"+ Add {comp}", key=f"add_{comp}_{current_symbol}", width="stretch", type="primary"):
                    # Create new conversation for this stock
                    query = f"Give me a quick analysis of {comp}"
                    
                    st.session_state.stock_conversations[comp] = {
                        "messages": [{"role": "user", "content": query}],
                        "stock_data": stock_data
                    }
                    save_conversations()
                    
                    # Start background analysis
                    future = st.session_state.executor.submit(run_analysis_task, comp, query)
                    st.session_state.background_tasks[comp] = future
                    st.session_state.active_threads[comp] = True
                    
                    # Switch to the new stock
                    st.session_state.selected_stock = comp
                    st.session_state.selected_view = "chat"
                    st.rerun()

