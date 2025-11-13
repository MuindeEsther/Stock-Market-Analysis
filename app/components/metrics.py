import pandas as pd
import numpy as np
import logging
from utils.config import TRADING_DAYS_PER_YEAR

logger = logging.getLogger(__name__)


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
        'Volatility': returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR),
        'Sharpe_Ratio': calculate_sharpe_ratio(returns),
        'Max_Drawdown': calculate_max_drawdown(returns)
    }
    
    return stats


def calculate_portfolio_metrics(data_dict, weights=None):
    """
    Calculate portfolio-level metrics.
    
    Args:
        data_dict (dict): Dictionary of stock DataFrames
        weights (dict): Dictionary of weights for each stock (must sum to 1)
    
    Returns:
        dict: Portfolio metrics
    """
    if not data_dict:
        logger.warning("Empty data dictionary provided")
        return None
    
    # Default equal weights
    if weights is None:
        weights = {name: 1/len(data_dict) for name in data_dict.keys()}
    
    # Validate weights sum to 1
    weight_sum = sum(weights.values())
    if not np.isclose(weight_sum, 1.0):
        logger.warning(f"Weights sum to {weight_sum}, normalizing to 1.0")
        weights = {k: v/weight_sum for k, v in weights.items()}
    
    # Extract returns
    returns_df = pd.DataFrame({
        name: data['Daily_Return'] 
        for name, data in data_dict.items()
    }).dropna()
    
    if returns_df.empty:
        logger.error("No valid returns data found")
        return None
    
    # Calculate portfolio returns
    portfolio_returns = sum(returns_df[name] * weights.get(name, 0) 
                           for name in returns_df.columns)
    
    # Calculate metrics
    metrics = {
        'Total_Return': (portfolio_returns + 1).prod() - 1,
        'Annualized_Return': portfolio_returns.mean() * TRADING_DAYS_PER_YEAR,
        'Annualized_Volatility': portfolio_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR),
        'Sharpe_Ratio': calculate_sharpe_ratio(portfolio_returns),
        'Sortino_Ratio': calculate_sortino_ratio(portfolio_returns),
        'Max_Drawdown': calculate_max_drawdown(portfolio_returns),
        'Calmar_Ratio': calculate_calmar_ratio(portfolio_returns),
        'Correlation_Matrix': returns_df.corr(),
        'Portfolio_Beta': calculate_portfolio_beta(returns_df, weights),
        'Value_at_Risk_95': calculate_var(portfolio_returns, confidence=0.95),
        'Conditional_VaR_95': calculate_cvar(portfolio_returns, confidence=0.95)
    }
    
    return metrics


def calculate_max_drawdown(returns):
    """
    Calculate maximum drawdown from returns series.
    
    Args:
        returns (pd.Series): Daily returns
    
    Returns:
        float: Maximum drawdown (negative value)
    """
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()


def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """
    Calculate Sharpe Ratio (risk-adjusted return).
    
    Args:
        returns (pd.Series): Daily returns
        risk_free_rate (float): Annual risk-free rate (default 2%)
    
    Returns:
        float: Sharpe ratio
    """
    if returns.std() == 0:
        return 0
    
    excess_returns = returns.mean() * TRADING_DAYS_PER_YEAR - risk_free_rate
    annualized_vol = returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    
    return excess_returns / annualized_vol


def calculate_sortino_ratio(returns, risk_free_rate=0.02):
    """
    Calculate Sortino Ratio (downside risk-adjusted return).
    
    Args:
        returns (pd.Series): Daily returns
        risk_free_rate (float): Annual risk-free rate
    
    Returns:
        float: Sortino ratio
    """
    excess_returns = returns.mean() * TRADING_DAYS_PER_YEAR - risk_free_rate
    downside_returns = returns[returns < 0]
    
    if len(downside_returns) == 0 or downside_returns.std() == 0:
        return 0
    
    downside_deviation = downside_returns.std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    
    return excess_returns / downside_deviation


def calculate_calmar_ratio(returns):
    """
    Calculate Calmar Ratio (return over max drawdown).
    
    Args:
        returns (pd.Series): Daily returns
    
    Returns:
        float: Calmar ratio
    """
    annualized_return = returns.mean() * TRADING_DAYS_PER_YEAR
    max_dd = abs(calculate_max_drawdown(returns))
    
    if max_dd == 0:
        return 0
    
    return annualized_return / max_dd


def calculate_var(returns, confidence=0.95):
    """
    Calculate Value at Risk (VaR).
    
    Args:
        returns (pd.Series): Daily returns
        confidence (float): Confidence level (e.g., 0.95 for 95%)
    
    Returns:
        float: VaR value (negative indicates loss)
    """
    return np.percentile(returns, (1 - confidence) * 100)


def calculate_cvar(returns, confidence=0.95):
    """
    Calculate Conditional Value at Risk (CVaR/Expected Shortfall).
    
    Args:
        returns (pd.Series): Daily returns
        confidence (float): Confidence level
    
    Returns:
        float: CVaR value (average of returns below VaR)
    """
    var = calculate_var(returns, confidence)
    return returns[returns <= var].mean()


def calculate_portfolio_beta(returns_df, weights, market_col='S&P 500'):
    """
    Calculate portfolio beta relative to market.
    
    Args:
        returns_df (pd.DataFrame): Returns for all assets
        weights (dict): Portfolio weights
        market_col (str): Column name for market returns
    
    Returns:
        float: Portfolio beta (None if market data unavailable)
    """
    if market_col not in returns_df.columns:
        logger.warning(f"Market column '{market_col}' not found")
        return None
    
    portfolio_returns = sum(returns_df[col] * weights.get(col, 0) 
                           for col in returns_df.columns if col != market_col)
    
    market_returns = returns_df[market_col]
    
    covariance = portfolio_returns.cov(market_returns)
    market_variance = market_returns.var()
    
    if market_variance == 0:
        return None
    
    return covariance / market_variance


def calculate_rolling_metrics(data, window=20):
    """
    Calculate rolling performance metrics.
    
    Args:
        data (pd.DataFrame): Stock data with returns
        window (int): Rolling window size
    
    Returns:
        pd.DataFrame: Data with rolling metrics added
    """
    df = data.copy()
    returns = df['Daily_Return']
    
    df[f'Rolling_Return_{window}d'] = returns.rolling(window=window).sum()
    df[f'Rolling_Volatility_{window}d'] = returns.rolling(window=window).std() * np.sqrt(TRADING_DAYS_PER_YEAR)
    df[f'Rolling_Sharpe_{window}d'] = (
        returns.rolling(window=window).mean() * TRADING_DAYS_PER_YEAR / 
        (returns.rolling(window=window).std() * np.sqrt(TRADING_DAYS_PER_YEAR))
    )
    
    return df


def compare_stocks(data_dict, metric='Total_Return'):
    """
    Compare multiple stocks based on a specific metric.
    
    Args:
        data_dict (dict): Dictionary of stock DataFrames
        metric (str): Metric to compare ('Total_Return', 'Volatility', 'Sharpe_Ratio')
    
    Returns:
        pd.DataFrame: Comparison table sorted by metric
    """
    comparison = []
    
    for name, data in data_dict.items():
        stats = get_summary_statistics(data)
        if stats:
            comparison.append({
                'Stock': name,
                'Total_Return': stats['Total_Return'],
                'Volatility': stats['Volatility'],
                'Sharpe_Ratio': stats['Sharpe_Ratio'],
                'Max_Drawdown': stats['Max_Drawdown'],
                'Current_Price': stats['Current_Price']
            })
    
    df = pd.DataFrame(comparison)
    
    if not df.empty and metric in df.columns:
        df = df.sort_values(by=metric, ascending=False)
    
    return df


def calculate_correlation_summary(data_dict):
    """
    Calculate correlation summary between all stocks.
    
    Args:
        data_dict (dict): Dictionary of stock DataFrames
    
    Returns:
        pd.DataFrame: Correlation matrix
    """
    returns_df = pd.DataFrame({
        name: data['Daily_Return'] 
        for name, data in data_dict.items()
    }).dropna()
    
    return returns_df.corr()