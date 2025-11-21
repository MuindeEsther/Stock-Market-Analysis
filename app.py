import streamlit as st
import pandas as pd
import logging
import time
from datetime import datetime

# Local import (placeholder for actual local module)
from app.utils import config
from app.utils.data_loader import get_data, get_multiple_tickers, get_fundamentals
from app.components import charts, alerts
from app.utils import indicators # as indicators_module
from app.components import metrics as metrics_module

# Set up logging
logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

# Set up page config
st.set_page_config(page_title=config.PAGE_TITLE,
                   page_icon=config.PAGE_ICON,
                   layout="wide",
                   initial_sidebar_state="expanded"
                    )

# Helper / UI utility funcs

@st.cache_data(ttl=int(config.CACHE_TTL.total_seconds()))
def load_ticker_data(symbol: str, period: str = config.DEFAULT_PERIOD, interval: str = config.DEFAULT_INTERVAL):
    # Load single ticker data (with indicators). Cached for performance.
    return get_data(symbol, period=period, interval=interval, include_indicators=True)

@st.cache_data(ttl=int(config.CACHE_TTL.total_seconds()))
def load_multiple_watchlist(tickers_dict, period: str = config.DEFAULT_PERIOD, interval: str = config.DEFAULT_INTERVAL):
    # Load multiple tickers (dictionary)
    return get_multiple_tickers(tickers_dict, period=period, interval=interval, include_indicators=True)

# Sidebar controls
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("Confirgure the dashboard and data refresh options below.")

# Ticker selector (friendly names from config.TICKERS)
names = list(config.TICKERS.keys())
default_name = "Apple" if "Apple" in names else names[0]
selected_name = st.sidebar.selectbox("Select asset (friendly name):", names, index=names.index(default_name))
selected_symbol = config.TICKERS[selected_name]

# Period & Interval
period = st.sidebar.selectbox("Period", options=["1mo", "3mo", "6mo", "1y", "2y"], index=3)
interval = st.sidebar.selectbox("Interval", options=["1d", "1wk", "1mo"], index=0)

# NSE comparison toggle
compare_nse = st.sidebar.checkbox("Compare with NSE Index", value=True)

# Quick watchlist selection and refresh
st.sidebar.markdown("### 📋 Watchlist")
if "watchlist" not in st.session_state:
    st.session_state.watchlist = ["Apple", "S&P 500", "Kenya Market Index (NSE20)"]
    
if st.sidebar.button("Add selected to Watchlist"):
    if selected_name not in st.session_state.watchlist:
        st.session_state.watchlist.append(selected_name)
        
if st.sidebar.button("Refresh data"):
    # Simple force-refresh by clearing cache
    st.cache_data.clear()
    st.experimental_rerun()
    
st.sidebar.markdown("**Current Watchlist:**")
st.sidebar.write(", ".join(st.session_state.watchlist))

# Main layour header

st.title("📈 Real-Time Global & Kenyan Market Dashboard")
st.markdown(
    "Live Price monitoring, technical indicator, and local (NSE) vs global comparisons."
    "This is a research / prototype dashboard - not a financial advice."
)

# Load data

with st.spinner(config.MESSAGES['loading']):
    df = load_ticker_data(selected_symbol, period=period, interval=interval)

# validate data
if df is None or df.empty:
    st.error(f"{config.MESSAGES['no_data']} for {selected_name} ({selected_symbol})")
    st.stop()
    
# Ensure datetime index for plotting
if 'Date' in df.columns:
    df.set_index(pd.to_datetime(df['Date']), inplace=True, drop=True)
elif not isinstance(df.index, pd.DatetimeIndex):
    try:
        df.index = pd.to_datetime(df.index)
    except Exception:
        pass

# KPIs / Summary cards

st.subheader(f"📊 Key Performance Indicators for {selected_name} ({selected_symbol})")

try:
    # Use metrics module (user provided). If their module name is different adjust import.
    summary = metrics_module.get_summary_statistics(df)
except Exception as e:
    logger.warning("metrics.get_summary_statistics failed, using default implementation.", e)
    # fallback minimal summary
    summary = {
        "Current_Price": float(df['Close'].iloc[-1]),
        "Change_Percent": float(((df['Close'].iloc[-1] / df['Close'].iloc[-2]) - 1) * 100) if len(df) > 1 else 0,
        "Total_Return": float(((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100)
    }

col1, col2, col3, col4= st.columns(4)
col1.metric("Price", f"{summary.get('Current_Price'):.2f}", delta=f"{summary.get('Change_Percent'):.2f}%")
col2.metric("24h Change %", f"{summary.get('Change_Percent'):.2f}%", delta=None)
col3.metric("Total Return (period)", f"{summary.get('Total_Return'):.2f}%")
col4.metric("Volatility (ann.)", f"{summary.get('Volatility'):.2f}" if summary.get('Volatility') is not None else "N/A")

# Fundamentals
with st.expander("Fundamentals (Yahoo)"):
    fundamentals = get_fundamentals(selected_symbol)
    if fundamentals:
        st.json(fundamentals)
    else:
        st.write("No fundamentals available.")

# Charts (price + indicators)

st.subheader("Price Chart & Technical Indicators")
fig_price = charts.plot_price_chart(df, f"{selected_name} ({selected_symbol})") # compare_nse=compare_nse)
st.plotly_chart(fig_price, use_container_width=True)

st.subheader("Volume")
fig_vol = charts.plot_volume_chart(df, f"{selected_name} ({selected_symbol})")
st.plotly_chart(fig_vol, use_container_width=True)

# Alerts
st.subheader("🚨 Alerts")
alert_list = alerts.generate_all_alerts(df, selected_name)
if alert_list:
    for a in alert_list:
         # choose severity visualization
        if a.startswith("🚀") or a.startswith("📈"):
            st.success(a)
        elif a.startswith("⚠️") or a.startswith("📉"):
             st.error(a)
        else:
            st.info(a)
else:
    st.write("No alerts at this time.")
    
# Cmparison panel (watchlist & NSE)

st.subheader("📋 Comparative Performance")

# Build comparsion dict from session watchlist 
watchlist_names = st.session_state.watchlist
watchlist_dict = {name: config.TICKERS.get(name, names) for name in watchlist_names if config.TICKERS.get(name, None) is not None}

with st.spinner("Loading watchlist data..."):
    watchlist_data = load_multiple_watchlist(watchlist_dict, period=period, interval=interval)
    
# Cumulative returns plot
if watchlist_data:
    fig_cum = charts.plot_cumulative_returns(watchlist_data, title="Cumulative Returns Comparison")
    st.plotly_chart(fig_cum, use_container_width=True)
else:
    st.write("No watchlist data available for comparison.")
    
# NSE special comparison
if compare_nse:
    st.subheader("NSE vs Global Index Comparison")
    # try to fetch NSE index (^NSE20) and S&P 500 (^GSPC)
    nse_symbol = config.TICKERS.get("Kenya Market Index (NSE20)") or config.TICKERS.get("Nairobi Securities Exchange")
    sp_symbol = config.TICKERS.get("S&P 500") or "^GSPC"
    try:
        nse_df = load_ticker_data(nse_symbol, period=period, interval=interval)
        sp_df = load_ticker_data(sp_symbol, period=period, interval=interval)
        # Prepare simple cumulative return serires
        def cumulative_from_close(d):
            s = d["Close"].pct_change().fillna(0) + 1
            return s.cumprod() - 1
        if nse_df is not None and not nse_df.empty and sp_df is not None and not sp_df.empty:
            comp_dict = {
                "NSE20": nse_df.assign(Cumulative_Return=cumulative_from_close(nse_df))['Cumulative_Return'],
                "S&P 500": sp_df.assign(Cumulative_Return=cumulative_from_close(sp_df))['Cumulative_Return']
            }
            # Convert to DataFrame
            comp_dfs = {k: d.to_frame(name='Cumulative_Return') if isinstance(d, pd.Series) else d for k, d in comp_dict.items()}
            # Reformat to DataFrame map like other functions
            comp_plot_map = {}
            for k, series in comp_dfs.items():
                if isinstance(series, pd.DataFrame) and 'Cumulative_Return' in series.columns:
                    tmp_df = pd.DataFrame({'Cumulative_Return': series['Cumulative_Return']})
                    tmp_df.index = nse_df.inde if k == "NSE20" else sp_df.index
                    comp_plot_map[k] = tmp_df
                    
            # plot
            st.plotly_chart(charts.plot_cumulative_returns(comp_plot_map, title="NSE20 vs S&P 500 Cumulative Returns"), use_container_width=True)
        else:
            st.info("NSE or S&P 500 data not available for comparison.")
    except Exception as e:
        logger.error("Error loading NSE or S&P 500 data for comparison.", exc_info=e)
        st.error("Failed to load NSE or S&P 500 data for comparison.")
        
# Footer / debug info

st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data provided by Yahoo Finance | Built with Streamlit""")

# Developer panel
with st.expander("Developer Panel"):
    st.write("Selected symbol:", selected_symbol)
    st.write("Data sample:")
    st.dataframe(df.tail().reset_index())
    st.write("Columnns:", df.columns.tolist())
    
           
           
           
    
        
