import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
# import logging  



def get_data(ticker, period="1y", interval="1d", include_indicators=True):
    """
    Fetch stock data with optional technical indicators.
    
    Args:
        ticker (str): Stock ticker symbol.
        period (str): Data period (e.g., '1d', '5d', '1mo',1y', '6mo').
        interval (str): Data interval (e.g., '1d', '1h').
        include_indicators (bool): Whether to include technical indicators.
    Returns:
        pd.DataFrame: DataFrame containing stock data with OHLCV and optional indicators.
        
    """
    try:
        logger.info(f"Fetching data for {ticker} for period: {period}, interval: {interval}")
        data = yf.download(ticker, period=period, interval=interval, progress=False)
        if data.empty:
            logger.warning(f"No data found for ticker: {ticker}")
            return None
        
        data.dropna(inplace=True)
        
        if include_indicators and len(data) > 0:
            data = add_technical_indicators(data)
            
        logger.info(f"Successfully fetched data for {len(data)} rows for {ticker}.")
        return data
    except Exception as e:
        logger.error(f"Error fetching data for {ticker}: {e}")
        return None
    
def add_technical_indicators(data):
    """
    Add technical indicators to the stock data.

    Args:
        data (pd.DataFrame): Stock OHLCV data.
        
    Returns:
        pd.DataFrame: DataFrame with added technical indicators.
    """
    df = data.copy()
    
    # Price-based indicators
    df['Daily_Return'] = df["Close"].pct_change()
    df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
    
    # Moving Averages
    df['MA_20'] = df['Close'].rolling(window=20).mean()
    df['MA_50'] = df['Close'].rolling(window=50).mean()
    df['MA_200'] = df['Close'].rolling(window=200).mean()
    
    # Exponential Moving Averages
    df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
    
    # RSI (Relative Strength Index)
    def calculate_rsi(series, window):
        # Calculate Relative Strength Index
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    df['RSI'] = calculate_rsi(df['Close'])
    
    # Volatility
    df['Volatility_20'] = df['Daily_Return'].rolling(window=20).std() * np.sqrt(252)
    df['Volatility_50'] = df['Daily_Return'].rolling(window=50).std() * np.sqrt(252)
    
    # Average True Range (ATR)
    def calculate_atr(df, window=14):
        # Calculate Average True Range
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=window).mean()
        return atr
    df['ATR'] = calculate_atr(df)
    
    return df

def get_fundamentals(ticker):
    """
    Fetch fundamental data for a given stock.
    
    Args:
        ticker (str): Stock ticker symbol.
    Returns:
        dict: Dictionary containing fundamental metrics.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        fundamentals = {
            'Name': info.get('longName', 'N/A'),
            'Sector': info.get('sector', 'N/A'),
            'Industry': info.get('industry', 'N/A'),
            'Market Cap': info.get('marketCap', 'N/A'),
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
            'Revenue_Growth': info.get('revenueGrowth'),
        }
        
        return fundamentals
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker}: {str(e)}")
        return None

def get_multiple_tickers(tickers_dict, period="1y", interval="1d", include_indicators=True):
    """
    Fetch data for multiple tickers.
    
    Args:
        tickers_dict (dict): Dictionary of ticker names and symbols.
        period (str): Data period.
        interval (str): Data interval.
        include_indicators (bool): Whether to include technical indicators.
    Returns:
        dict: Dictionary of DataFrames for each ticker.
    """
    data_dict = {}
    
    for name, symbol in tickers_dict.items():
        data = get_data(symbol, period, interval, include_indicators)
        if data is not None:
            data_dict[name] = data
        else:
            logger.warning(f"Skipping {name} ({symbol}) due to data fetch error.")
            
    return data_dict

def calculate_max_drawdown(returns):
    """Calculate maximum drawdown from returns series."""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def calculate_portfolio_metrics(data_dict, weights=None):
    """
    Calculate portfolio-level metrics.
    
    Args:
        data_dict (dict): Dictionary of DataFrames for each ticker.
        weights (dict): Dictionary of weights for each ticker.
    Returns:
        pd.DataFrame: DataFrame containing portfolio metrics.
    """
    if not data_dict:
        return None
    
    # Default equal weights
    if weights is None:
        weights = {name: 1/len(data_dict) for name in data_dict.keys()}
    
    # Extract returns
    returns_df = pd.DataFrame({
        name: data['Daily_Return'] 
        for name, data in data_dict.items()
    }).dropna()
    
    # Calculate portfolio returns
    portfolio_returns = sum(returns_df[name] * weights[name] for name, weight in weights.items())
    
    # Calculate metrics
    metrics = {
        'Total Return': portfolio_returns.sum(),#.iloc[-1],
        'Annualized_Return': portfolio_returns.mean() * 252,
        'Annualized_Volatility': portfolio_returns.std() * np.sqrt(252),
        'Sharpe_Ratio': (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252) if portfolio_returns.std() != 0 else np.nan,
        'Max_Drawdown': calculate_max_drawdown(portfolio_returns),
        'Correlation_Matrix': returns_df.corr()
    }
    return metrics

def get_summary_statistics(data):
    """
    Calculate summary statistics for stock data.
    
    Args:
        data (pd.DataFrame): Stock data
    
    Returns:
        dict: Summary statistics
    """
    if data is None or data.empty:
        return None
    
    returns = data['Daily_Return'].dropna()
    
    stats = {
        'Current_Price': data['Close'].iloc[-1],
        'Previous_Close': data['Close'].iloc[-2] if len(data) > 1 else None,
        'Change': data['Close'].iloc[-1] - data['Close'].iloc[-2] if len(data) > 1 else None,
        'Change_Percent': ((data['Close'].iloc[-1] / data['Close'].iloc[-2]) - 1) * 100 if len(data) > 1 else None,
        'High': data['High'].max(),
        'Low': data['Low'].min(),
        'Average_Volume': data['Volume'].mean(),
        'Total_Return': ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100,
        'Volatility': returns.std() * np.sqrt(252),
        'Sharpe_Ratio': (returns.mean() * 252) / (returns.std() * np.sqrt(252)) if returns.std() != 0 else 0,
        'Max_Drawdown': calculate_max_drawdown(returns)
    }
    
    return stats
            
    