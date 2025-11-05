# Stock-Market-Analysis
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

