# Stock-Market-Analysis

## 🌐 Live Dashboard

[Open the Global & Kenyan Market Dashboard](https://stock-market-analysis-7kgxyg2vnibsm56bf4xz6w.streamlit.app/)

Streamlit dashboard for real-time stock market visualization using Python + yfinance.

# 📈 Real-Time Global Market Intelligence Dashboard  
*A strategic fintech research project for investment decision support*

This project builds a real-time equity market intelligence dashboard designed for a fund management environment. It provides live prices, technical indicators, sector analytics, and alerting functionality to support tactical decision-making and long-term equity strategy development.

---

## 🎯 Problem Context

Investment teams monitor large volumes of fast-moving market information across multiple platforms. For smaller firms or teams in growth markets, access to institutional terminals (Bloomberg, Refinitiv) may be limited — especially to junior analysts. This slows:

- Market surveillance
- Early signal detection
- Equity opportunity screening
- Decision readiness during market events
- Internal research capacity building

---

## 🚀 Project Goal

Build an internal research tool that:

- Centralizes real-time market data  
- Visualizes actionable signals and trends  
- Enhances analyst productivity & learning  
- Improves the speed & clarity of decision support  
- Supports strategic readiness for a **Global Equity Fund**

---

## ✅ Business Hypothesis

> *A lightweight in-house market dashboard can supplement external tools by improving research agility, increasing monitoring frequency, and enabling proactive investment intelligence — at significantly lower cost.*

---

## 🔍 Research Questions

| Category | Questions |
|---|---|
User Pain Points | Where do analysts lose time when monitoring markets? |
Decision Workflow | What information do investment managers look at daily vs weekly? |
Data Needs | Which equity KPIs drive actionable decisions? |
Visuals | Which chart types accelerate interpretation? |
Strategic Fit | Does real-time monitoring support our global fund ambition? |
Impact | Can this tool enhance analyst skill development? |

---

## 🧠 Research Methodology

### **1. Qualitative Workflow Analysis**
- Interviewed investment analyst (informal discussion)
- Observed daily/weekly monitoring routines
- Mapped key data touchpoints: price → trend → risk → narrative
- Identified manual steps & duplicative tool use

**Key Finding:**  
Manual cross-platform price & chart checks slow early signal detection.

---

### **2. Benchmarking Study**
Benchmarked institutional trading terminals and retail research tools:

| Reference | Concepts Borrowed |
|---|---|
Bloomberg Terminal | Sector heatmaps, alerts |
Morningstar Direct | Portfolio risk metrics |
TradingView | Candlestick + MA visualization |
Yahoo Finance | Retail-grade data feed |

---

### **3. Technical Feasibility Study**
Evaluated Python packages & fintech infrastructure:

| Tool | Purpose |
|---|---|
`yfinance` | Market data |
`pandas` | Data cleaning & indicators |
`plotly` | Interactive market visuals |
`streamlit` | Real-time dashboard UI |

---

### **4. Product Requirements Definition**

| Stakeholder | Needs |
|---|---|
Investment Manager | Fast signal insight, visual context |
Analyst | Learning environment + watchlist alerts |
Board/CIO | Strategic market snapshots |

---

### **5. Proof-of-Concept Development**
- Iterative agile build  
- Feature priorities mapped to real workflows  
- Continuous validation with investment logic  

---

## 📊 Dashboard Features

### Core Features
- ✅ Live price monitoring  
- ✅ Candlestick charts w/ Moving Averages (MA20, MA50, MA200)  
- ✅ Sector & industry performance view  
- ✅ Daily return & volatility metrics  
- ✅ Watchlist & threshold alerts  

### Future Roadmap
- 🧠 Automated research commentary (AI)
- 💼 Portfolio tracking & attribution
- 🔔 Macro-signal dashboard (rates, FX, commodities)
- 📉 Risk engine (VaR, drawdowns, beta)
- 📈 Strategy backtesting

---

## 📂 Architecture

```
# app.py
import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

# --- CONFIGURATION ---
st.set_page_config(layout="wide")

# --- DATA LOADING ---
@st.cache_data
def load_data(ticker):
    data = yf.Ticker(ticker)
    df = data.history(period="1y")
    df.reset_index(inplace=True)
    return df

# --- LAYOUT ---
st.title("📈 Stock Market Dashboard")
ticker = st.sidebar.text_input("Enter Ticker", "AAPL")
df = load_data(ticker)

# --- PRICE CHART ---
st.subheader(f"{ticker} Price Chart")
fig = go.Figure()
fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'))
fig.add_trace(go.Scatter(x=df['Date'], y=df['Open'], mode='lines', name='Open'))
st.plotly_chart(fig)

# --- TECHNICAL INDICATORS ---
st.subheader("Technical Indicators")
ma_period = st.slider("Moving Average Period", 5, 50, 20)
df[f'MA{ma_period}'] = df['Close'].rolling(window=ma_period).mean()
fig_ma = go.Figure()
fig_ma.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Close'))
fig_ma.add_trace(go.Scatter(x=df['Date'], y=df[f'MA{ma_period}'], mode='lines', name=f'MA{ma_period}'))
st.plotly_chart(fig_ma)

# --- ALERTS ---
st.subheader("Price Alerts")
alert_price = st.number_input("Alert Price", min_value=0.0, value=150.0, step=1.0)
if st.button("Set Alert"):
    st.success(f"Alert set for ${alert_price}")

# --- FOOTER ---
st.markdown("---")
st.write("Data source: Yahoo Finance")
```

---

## Deployment

### Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`.

### Features

- Global and Kenyan market selection
- Candlestick, volume, Bollinger, moving-average, RSI, MACD, and stochastic charts
- Configurable price alerts and watchlist URL persistence
- NSE 20 versus S&P 500 comparison
- CSV export for selected asset data
- Cached Yahoo Finance data for faster refreshes

### Test

```powershell
python -m pip install pytest
python -m pytest -q
```

### Deploy on Streamlit Community Cloud

1. Push the project to GitHub.
2. Open Streamlit Community Cloud and choose **Create app**.
3. Select this repository and set the main file to `app.py`.
4. Choose a public or private app URL and deploy.
5. Ensure `requirements.txt` remains at the repository root.

No secrets or API keys are required because the app uses Yahoo Finance public data endpoints.

