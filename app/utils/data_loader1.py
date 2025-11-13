# data_loader.py
"""
Data loading module for fetching stock market data from Yahoo Finance.
Handles data retrieval and basic preprocessing.
"""

import yfinance as yf
import pandas as pd
import logging
from .config import TICKERS, DEFAULT_PERIOD, DEFAULT_INTERVAL
from .indicators import add_technical_indicators

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_data(ticker, period=DEFAULT_PERIOD, interval=DEFAULT_INTERVAL, include_indicators=True):
    """
    Fetch stock data with optional technical indicators.
    
    Args:
        ticker (str): Stock ticker symbol
        period (str): Data period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        interval (str): Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        include_indicators (bool): Whether to calculate technical indicators
    
    Returns:
        pd.DataFrame: Stock data with OHLCV and optional indicators
    """
    try:
        logger.info(f"Fetching data for {ticker}...")
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        
        if data.empty:
            logger.warning(f"No data returned for {ticker}")
            return None
        
        data.dropna(inplace=True)
        
        # Add basic return calculation
        data['Daily_Return'] = data['Close'].pct_change()
        data['Cumulative_Return'] = (1 + data['Daily_Return']).cumprod() - 1
        
        if include_indicators and len(data) > 0:
            data = add_technical_indicators(data)
        
        logger.info(f"Successfully fetched {len(data)} rows for {ticker}")
        return data
        
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {str(e)}")
        return None


def get_fundamentals(ticker):
    """
    Fetch fundamental data for a stock.
    
    Args:
        ticker (str): Stock ticker symbol
    
    Returns:
        dict: Fundamental metrics
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        fundamentals = {
            'Name': info.get('longName', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Market_Cap': info.get('marketCap'),
            'PE_Ratio': info.get('trailingPE'),
            'Forward_PE': info.get('forwardPE'),
            'PEG_Ratio': info.get('pegRatio'),
            'Price_to_Book': info.get('priceToBook'),
            'Dividend_Yield': info.get('dividendYield'),
            'Dividend_Rate': info.get('dividendRate'),
            'Beta': info.get('beta'),
            'EPS': info.get('trailingEps'),
            '52_Week_High': info.get('fiftyTwoWeekHigh'),
            '52_Week_Low': info.get('fiftyTwoWeekLow'),
            'Average_Volume': info.get('averageVolume'),
            'Profit_Margins': info.get('profitMargins'),
            'Revenue_Growth': info.get('revenueGrowth')
        }
        
        logger.info(f"Successfully fetched fundamentals for {ticker}")
        return fundamentals
        
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker}: {str(e)}")
        return None


def get_multiple_tickers(tickers_dict=None, period=DEFAULT_PERIOD, interval=DEFAULT_INTERVAL, include_indicators=True):
    """
    Fetch data for multiple tickers.
    
    Args:
        tickers_dict (dict): Dictionary of ticker names and symbols (defaults to TICKERS from config)
        period (str): Data period
        interval (str): Data interval
        include_indicators (bool): Whether to include technical indicators
    
    Returns:
        dict: Dictionary of DataFrames keyed by ticker name
    """
    if tickers_dict is None:
        tickers_dict = TICKERS
    
    data_dict = {}
    
    for name, symbol in tickers_dict.items():
        data = get_data(symbol, period, interval, include_indicators)
        if data is not None:
            data_dict[name] = data
        else:
            logger.warning(f"Skipping {name} due to data fetch error")
    
    return data_dict


def validate_data(data):
    """
    Validate that fetched data meets minimum requirements.
    
    Args:
        data (pd.DataFrame): Stock data to validate
    
    Returns:
        bool: True if data is valid, False otherwise
    """
    if data is None or data.empty:
        return False
    
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in data.columns for col in required_columns):
        logger.error("Data missing required columns")
        return False
    
    if len(data) < 2:
        logger.error("Insufficient data points")
        return False
    
    return True