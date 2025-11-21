from datetime import timedelta

# Kenyan & global watchlist
TICKERS = {
    "Kenya Market Index (NSE20)": "^NSE20",
    "Safaricom": "SCOM.NR",
    "Equity Group": "EQTY.NR",
    "KCB": "KCB.NR",
    "S&P 500": "^GSPC",
    "NASDAQ": "^IXIC",
    "Apple": "AAPL",
    "Microsoft": "MSFT"
}

# Trading days per year (for annualization calculations)
TRADING_DAYS_PER_YEAR = 252

# Default periods for data fetching
DEFAULT_PERIOD = "1y"
DEFAULT_INTERVAL = "1d"

# Technical indicator parameters
INDICATOR_PARAMS = {
    "RSI_PERIOD": 14,
    "ATR_PERIOD": 14,
    "MA_SHORT": 20,
    "MA_MEDIUM": 50,
    "MA_LONG": 200,
    "EMA_FAST": 12,
    "EMA_SLOW": 26,
    "MACD_SIGNAL": 9,
    "BOLLINGER_PERIOD": 20,
    "BOLLINGER_STD": 2,
    "VOLATILITY_SHORT": 20,
    "VOLATILITY_LONG": 50
}

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


# Page configuration
PAGE_TITLE = "📈 Global & Kenyan Market Dashboard"
PAGE_ICON = "📊"

# Cache TTL (time-to-live) for streamlit cache
CACHE_TTL = timedelta(hours=1)

# UI Messages
MESSAGES = {
    "loading": "Loading data...",
    "no_data": "No data available"
}