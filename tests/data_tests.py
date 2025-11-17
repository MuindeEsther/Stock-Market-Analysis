import pytest
from app.utils.data_loader import get_data
from app.utils.config import TICKERS
import pandas as pd

def test_get_single_ticker():
    # Test that data is returned for a valid ticker.
    df = get_data(TICKERS["Apple"], period="1mo", interval="1d")
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns
    

def test_invalid_ticker_returns_empty_df():
    # Test behavior when ticker does not exist
    df = get_data("INVALID1234")
    assert isinstance(df, pd.DataFrame)
    assert df.empty or "Close" in df.columns 
    
def test_multiple_tickers():
    # Test fecthing data for more than one ticker
    tickers = [TICKERS["Apple"], TICKERS["Microsoft"]]
    combined_df = get_data(tickers, period="1mo", interval="1d")
    
    assert isinstance(combined_df, pd.DataFrame)
    assert not combined_df.empty
    assert "Ticker" in combined_df.columns
    assert combined_df["Ticker"].nunique() == 2
