import pandas as pd
import logging

logger = logging.getLogger(__name__)

def price_alerts(data: pd.DataFrame, stock_name: str, threshold: float = 0.05):
    
    """
    Generate price alerts when the stock price crosses a certain threshold.
    
    Args:
        data (pd.DataFrame): Stock data with 'Close' prices
        stock_name (str): Name of the stock
        threshold (float): Price threshold for alerts
    Returns:
        list: List of alert messages
    """
    
    alerts = []
    
    try:
        if data is None or data.empty:
            return ["⚠️ No data available to generate alerts."]
        
        # Calculate daily returns
        if 'Daily_Return' not in data.columns:
            data['Daily_Return'] = data['Close'].pct_change()
            
        latest_return = data['Daily_Return'].iloc[-1]
        
        if latest_return >= threshold:
            alerts.append(f"📈 {stock_name} jumped {latest_return:.2%} today!")
        elif latest_return <= -threshold:
            alerts.append(f"📉 {stock_name} dropped {latest_return:.2%} today!")
    except Exception as e:
        logger.error(f"Error generating price alerts for {stock_name}: {str(e)}")
        alerts.append(f"⚠️ Error generating alerts for {stock_name}.")
    return alerts

def moving_average_crossover_alert(data: pd.DataFrame, stock_name: str):
    """
    Detect moving average crossovers (short-term vs long-term trend shift).
    
    Args:
        data (pd.DataFrame): Must contain MA_20 and MA_50 columns.
        stock_name (str): Name of the stock.

    Returns:
        list: List of crossover alerts.
    """
    alerts = []
    try:
        if 'MA_20' not in data.columns or 'MA_50' not in data.columns:
            return ["ℹ️ Moving average data not available."]

        ma_short = data['MA_20'].iloc[-1]
        ma_long = data['MA_50'].iloc[-1]
        prev_ma_short = data['MA_20'].iloc[-2]
        prev_ma_long = data['MA_50'].iloc[-2]

        # Detect crossover events
        if prev_ma_short < prev_ma_long and ma_short > ma_long:
            alerts.append(f"📈 Bullish crossover detected on {stock_name} — potential upward trend.")
        elif prev_ma_short > prev_ma_long and ma_short < ma_long:
            alerts.append(f"📉 Bearish crossover detected on {stock_name} — possible trend reversal.")

    except Exception as e:
        logger.error(f"Error detecting MA crossover for {stock_name}: {e}")
        alerts.append("⚠️ Error detecting crossover alert.")

    return alerts

def volatility_alert(data: pd.DataFrame, stock_name: str, threshold: float = 0.03):
    """
    Generate volatility alerts when daily price range exceeds a threshold.
    """
    alerts = []
    try:
        if data is None or data.empty:
            return ["⚠️ No data to calculate volatility."]

        data['Volatility'] = (data['High'] - data['Low']) / data['Open']
        latest_volatility = data['Volatility'].iloc[-1]

        if latest_volatility > threshold:
            alerts.append(f"⚡ {stock_name} showed high volatility today ({latest_volatility:.2%}).")

    except Exception as e:
        logger.error(f"Error generating volatility alerts for {stock_name}: {e}")
        alerts.append("⚠️ Error generating volatility alert.")

    return alerts


def generate_all_alerts(data: pd.DataFrame, stock_name: str):
    """
    Aggregate all alert types for a given stock.
    """
    alerts = []
    alerts.extend(price_alerts(data, stock_name))
    alerts.extend(moving_average_crossover_alert(data, stock_name))
    alerts.extend(volatility_alert(data, stock_name))
    return alerts
        