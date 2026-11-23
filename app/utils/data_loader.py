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
        # Ensure ticker is a string, not a list
        if isinstance(ticker, list):
            logger.error("get_data() accepts a single ticker string, not a list.")
            return None
        
        logger.info(f"Fetching data for {ticker}...")
        data = yf.download(ticker, period=period, interval=interval, progress=False)

        if data.empty:
            logger.warning(f"No data returned for {ticker}")
            return None
        
        data.dropna(inplace=True)

        if isinstance(data.columns, pd.MultiIndex):
            # Extract the first level of column names
            data.columns = data.columns.get_level_values(0)
        
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
        info = stock.info or {}

        def first_value(keys):
            for key in keys:
                value = info.get(key)
                if value not in (None, "", "N/A"):
                    return value
            return None

        try:
            fast = stock.fast_info
        except Exception:
            fast = {}

        def fast_value(key):
            try:
                if hasattr(fast, "get"):
                    value = fast.get(key)
                    if value not in (None, ""):
                        return value
                return getattr(fast, key, None)
            except Exception:
                return None

        market_price = fast_value("last_price") or fast_value("regular_market_price")

        eps = first_value(["trailingEps", "epsTrailingTwelveMonths"])
        if eps is None:
            try:
                income = stock.income_stmt
                if income is not None and not income.empty:
                    for row in ("Diluted EPS", "Basic EPS"):
                        if row in income.index:
                            eps = float(income.loc[row].dropna().iloc[0])
                            if pd.notna(eps):
                                break
            except Exception:
                pass

        shares = fast_value("shares")
        market_cap = first_value(["marketCap", "market_cap"]) or fast_value("market_cap")
        if market_cap is None and market_price is not None and shares:
            market_cap = market_price * shares

        trailing_pe = first_value(["trailingPE", "trailing_pe"])
        if trailing_pe is None and market_price is not None and eps not in (None, 0):
            trailing_pe = market_price / eps

        forward_pe = first_value(["forwardPE", "forward_pe"])

        week_high = first_value(["fiftyTwoWeekHigh"]) or fast_value("year_high")
        week_low = first_value(["fiftyTwoWeekLow"]) or fast_value("year_low")
        if (week_high is None or week_low is None) and year_data is not None and not year_data.empty:
            week_high = week_high or float(year_data["High"].max())
            week_low = week_low or float(year_data["Low"].min())

        fundamentals = {
            'Name': first_value(["longName", "shortName", "name"]) or ticker,
            'Sector': first_value(["sector", "category"]) or "N/A",
            'Industry': first_value(["industry", "industryDisp"]) or "N/A",
            'Market_Cap': market_cap,
            'PE_Ratio': trailing_pe,
            'Forward_PE': forward_pe,
            'PEG_Ratio': first_value(["pegRatio"]),
            'Price_to_Book': first_value(["priceToBook", "price_to_book"]),
            'Dividend_Yield': first_value(["dividendYield", "yield"]),
            'Dividend_Rate': first_value(["dividendRate"]),
            'Beta': first_value(["beta"]),
            'EPS': eps,
            '52_Week_High': week_high,
            '52_Week_Low': week_low,
            'Average_Volume': first_value(["averageVolume", "averageVolume10days"]),
            'Profit_Margins': first_value(["profitMargins"]),
            'Revenue_Growth': first_value(["revenueGrowth"])
        }
        
        logger.info(f"Successfully fetched fundamentals for {ticker}")
        return fundamentals
        
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker}: {str(e)}")
        return None


def get_multiple_tickers(tickers_dict, period=DEFAULT_PERIOD, interval=DEFAULT_INTERVAL, include_indicators=True):
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

def get_local_kenyan_data(ticker, include_indicators=True):
    
    import os
    
    filepath = os.path.join("data", "processed", "Kenya", f"{ticker}.csv")
    
    if not os.path.exists(filepath):
        logger.error(f"Local Kenyan data file not found: {filepath}")
        return None
    
    try:
        data = pd.read_csv(filepath, parse_dates=["Date"])
        data.set_index("Date", inplace=True)
        
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in data.columns for col in required_cols):
            logger.error(f"Kenyan data missing required columns: {required_cols}")
            return None
        
        # Calculate returns
        data['Daily_Return'] = data['Close'].pct_change()
        data['Cumulative_Return'] = (1 + data['Daily_Return']).cumprod() - 1
        
        # Add indicators
        if include_indicators:
            data = add_technical_indicators(data)
            
        logger.info(f"Loaded Kenyan market data for {ticker}, rows: {len(data)}")
        return data
    
    except Exception as e:
        logger.error(f"Error loading Kenyan data for {ticker}: {str(e)}")
        return None

# Get multiple Kenyan tickers
def get_multiple_kenyan_tickers(tickers_dict):
    data_dict = {}
    
    for name, symbol in tickers_dict.items():
        data = get_local_kenyan_data(symbol)
        if data is not None:
            data_dict[name] = data
        else:
            logger.warning(f"Skipping {name} due to missing data")
    
    return data_dict