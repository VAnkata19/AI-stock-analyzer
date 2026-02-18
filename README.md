# Fintellix

Stop drowning in financial noise. Fintellix gives you instant, AI-driven stock research — real-time data, technical analysis, and competitor breakdowns — all in a conversational interface that makes sense whether you're a seasoned investor or just getting started.

## Overview

Fintellix is an AI-powered stock research assistant that lets you ask plain-English questions about any stock and get actionable answers backed by live market data. It combines GPT-4-level reasoning with real-time Yahoo Finance data, interactive Plotly charts, and a full suite of technical indicators — wrapped in a clean Streamlit UI. Whether you want a quick sentiment check or a deep technical breakdown, Fintellix handles it in one place.

## Short Demo:

https://github.com/user-attachments/assets/e31949ad-9399-456f-86e0-36dbc9fae4be

## Features

- **AI-Powered Analysis** — Ask questions about any stock and get detailed insights powered by GPT-4
- **Interactive Charts** — Candlestick and line charts with volume data using Plotly
- **Technical Analysis** — RSI, MACD, Bollinger Bands, and Moving Averages with signal summaries
- **Competitor Comparison** — Compare stocks against their competitors with AI-generated analysis
- **Beginner Mode** — Simplified explanations with ratings, risk levels, and actionable advice
- **Chat History** — Persistent conversations saved locally
- **Real-time Data** — Stock data from Yahoo Finance (yfinance)

## Tech Stack

- **Frontend**: Streamlit
- **AI/LLM**: LangChain + OpenAI GPT-4 Turbo
- **Charts**: Plotly
- **Stock Data**: Yahoo Finance (yfinance)
- **Web Search**: Tavily API

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fintellix.git
cd fintellix
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Or with uv:
uv pip install -r pyproject.toml
```

3. Create a `.env` file with your API keys:
```env
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

4. Run the app:
```bash
streamlit run app.py
```

## Usage

1. **Analyze a Stock** — Type a company name or ticker symbol in the chat (e.g., "Analyze Apple" or "How is TSLA doing?")
2. **View Charts** — Switch to the Chart tab to see price history
3. **Technical Analysis** — Disable Beginner Mode in Settings to access technical indicators
4. **Compare Competitors** — Go to the Competitors tab to see AI-powered comparisons

