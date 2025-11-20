import pytest
from app.utils.data_loader import get_data, get_multiple_tickers, validate_data
from app.utils.config import TICKERS
import pandas as pd

def test_get_single_ticker():
    # Test that data is returned for a valid ticker.
    df = get_data(TICKERS["Apple"], period="1mo", interval="1d")

    assert df is not None
    assert isinstance(df, pd.DataFrame)
    assert not df.empty

    required_columns = ["Open", "High", "Low", "Close", "Volume", "Daily_Return", "Cumulative_Return"]
    for col in required_columns:
        assert col in df.columns, f"{col}"
   
    

def test_invalid_ticker_returns_empty_df():
    # Test behavior when ticker does not exist
    df = get_data("INVALID1234")
    assert df is None, "Invalid ticker should return None"
    
def test_multiple_tickers():
    # Test fecthing data for more than one ticker
    tickers_dict = {
        "Apple": TICKERS["Apple"],
        "Microsoft": TICKERS["Microsoft"]
        }
    combined_data = get_multiple_tickers(tickers_dict, period="1mo", interval="1d")
    
    assert isinstance(combined_data, dict)
    assert len(combined_data) > 0

    # Check that each value is a DataFrame with required columns
    for name, df in combined_data.items():
        assert isinstance(df, pd.DataFrame), f"{name} data should be a DataFrame"
        required_columns = ["Open", "High", "Low", "Close", "Volume", "Daily_Return", "Cumulative_Return"]
        for col in required_columns:
            assert col in df.columns, f"{col} should exist in {name}'s DataFrame"
            
def test_validate_data():
    # Test the validate_data function
    
    df = get_data(TICKERS["Apple"], period="1mo", interval="1d")
    if df is not None:  # Only test if data fetch succeeded
        valid = validate_data(df)
        assert valid is True, "Valid DataFrame should pass validation"
    
    empty_df = pd.DataFrame()
    assert validate_data(empty_df) is False
    assert validate_data(None) is False

    # Test with DataFrame missing required columns
    invalid_df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
    assert validate_data(invalid_df) is False, "DataFrame without required columns should fail validation"
    

    # Test with DataFrame having required columns but insufficient data
    insufficient_df = pd.DataFrame({
        "Open": [100],
        "High": [105],
        "Low": [95],
        "Close": [102],
        "Volume": [1000000]
    })
    assert validate_data(insufficient_df) is False, "DataFrame with less than 2 rows should fail validation"
