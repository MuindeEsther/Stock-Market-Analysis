# indicators.py
"""
Technical indicators module for stock market analysis.
Contains functions to calculate various technical analysis indicators.
"""

import pandas as pd
import numpy as np
from .config import INDICATOR_PARAMS, TRADING_DAYS_PER_YEAR


def add_technical_indicators(data):
    """
    Add technical indicators to stock data.
    
    Args:
        data (pd.DataFrame): Stock OHLCV data
    
    Returns:
        pd.DataFrame: Data with technical indicators added
    """
    df = data.copy()
    
    # Moving Averages
    df['MA_20'] = df['Close'].rolling(window=INDICATOR_PARAMS['MA_SHORT']).mean()
    df['MA_50'] = df['Close'].rolling(window=INDICATOR_PARAMS['MA_MEDIUM']).mean()
    df['MA_200'] = df['Close'].rolling(window=INDICATOR_PARAMS['MA_LONG']).mean()
    
    # Exponential Moving Averages
    df['EMA_12'] = df['Close'].ewm(span=INDICATOR_PARAMS['EMA_FAST'], adjust=False).mean()
    df['EMA_26'] = df['Close'].ewm(span=INDICATOR_PARAMS['EMA_SLOW'], adjust=False).mean()
    
    # MACD
    df['MACD'] = df['EMA_12'] - df['EMA_26']
    df['MACD_Signal'] = df['MACD'].ewm(span=INDICATOR_PARAMS['MACD_SIGNAL'], adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    # Bollinger Bands
    df = add_bollinger_bands(df)
    
    # RSI (Relative Strength Index)
    df['RSI'] = calculate_rsi(df['Close'])
    
    # Volatility
    df['Volatility_20'] = df['Daily_Return'].rolling(
        window=INDICATOR_PARAMS['VOLATILITY_SHORT']
    ).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    
    df['Volatility_50'] = df['Daily_Return'].rolling(
        window=INDICATOR_PARAMS['VOLATILITY_LONG']
    ).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    
    # Average True Range (ATR)
    df['ATR'] = calculate_atr(df)
    
    # Stochastic Oscillator
    df = add_stochastic_oscillator(df)
    
    return df


def add_bollinger_bands(data, period=None, std_multiplier=None):
    """
    Add Bollinger Bands to the data.
    
    Args:
        data (pd.DataFrame): Stock data
        period (int): Rolling window period
        std_multiplier (float): Standard deviation multiplier
    
    Returns:
        pd.DataFrame: Data with Bollinger Bands added
    """
    if period is None:
        period = INDICATOR_PARAMS['BOLLINGER_PERIOD']
    if std_multiplier is None:
        std_multiplier = INDICATOR_PARAMS['BOLLINGER_STD']
    
    df = data.copy()
    df['BB_Middle'] = df['Close'].rolling(window=period).mean()
    bb_std = df['Close'].rolling(window=period).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * std_multiplier)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * std_multiplier)
    df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
    df['BB_Percent'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
    
    return df


def calculate_rsi(prices, period=None):
    """
    Calculate Relative Strength Index.
    
    Args:
        prices (pd.Series): Price series
        period (int): RSI period (default from config)
    
    Returns:
        pd.Series: RSI values
    """
    if period is None:
        period = INDICATOR_PARAMS['RSI_PERIOD']
    
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_atr(data, period=None):
    """
    Calculate Average True Range.
    
    Args:
        data (pd.DataFrame): Stock data with High, Low, Close columns
        period (int): ATR period (default from config)
    
    Returns:
        pd.Series: ATR values
    """
    if period is None:
        period = INDICATOR_PARAMS['ATR_PERIOD']
    
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr


def add_stochastic_oscillator(data, k_period=14, d_period=3):
    """
    Add Stochastic Oscillator to the data.
    
    Args:
        data (pd.DataFrame): Stock data
        k_period (int): %K period
        d_period (int): %D period
    
    Returns:
        pd.DataFrame: Data with Stochastic Oscillator added
    """
    df = data.copy()
    
    # Calculate %K
    low_min = df['Low'].rolling(window=k_period).min()
    high_max = df['High'].rolling(window=k_period).max()
    df['Stochastic_K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)
    
    # Calculate %D (moving average of %K)
    df['Stochastic_D'] = df['Stochastic_K'].rolling(window=d_period).mean()
    
    return df


def calculate_ema(prices, span):
    """
    Calculate Exponential Moving Average.
    
    Args:
        prices (pd.Series): Price series
        span (int): EMA span
    
    Returns:
        pd.Series: EMA values
    """
    return prices.ewm(span=span, adjust=False).mean()


def calculate_sma(prices, window):
    """
    Calculate Simple Moving Average.
    
    Args:
        prices (pd.Series): Price series
        window (int): SMA window
    
    Returns:
        pd.Series: SMA values
    """
    return prices.rolling(window=window).mean()


def identify_signals(data):
    """
    Identify buy/sell signals based on technical indicators.
    
    Args:
        data (pd.DataFrame): Stock data with indicators
    
    Returns:
        pd.DataFrame: Data with signal columns added
    """
    df = data.copy()
    
    # Moving Average Crossover signals
    df['MA_Signal'] = 0
    df.loc[df['MA_20'] > df['MA_50'], 'MA_Signal'] = 1  # Bullish
    df.loc[df['MA_20'] < df['MA_50'], 'MA_Signal'] = -1  # Bearish
    
    # RSI signals
    df['RSI_Signal'] = 0
    df.loc[df['RSI'] < 30, 'RSI_Signal'] = 1  # Oversold (buy)
    df.loc[df['RSI'] > 70, 'RSI_Signal'] = -1  # Overbought (sell)
    
    # MACD signals
    df['MACD_Signal_Flag'] = 0
    df.loc[df['MACD'] > df['MACD_Signal'], 'MACD_Signal_Flag'] = 1  # Bullish
    df.loc[df['MACD'] < df['MACD_Signal'], 'MACD_Signal_Flag'] = -1  # Bearish
    
    # Bollinger Bands signals
    df['BB_Signal'] = 0
    df.loc[df['Close'] < df['BB_Lower'], 'BB_Signal'] = 1  # Below lower band (buy)
    df.loc[df['Close'] > df['BB_Upper'], 'BB_Signal'] = -1  # Above upper band (sell)
    
    return df