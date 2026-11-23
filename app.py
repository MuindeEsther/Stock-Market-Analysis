import streamlit as st
import pandas as pd
import logging
from datetime import datetime

from app.utils import config
from app.utils.data_loader import get_data, get_multiple_tickers, get_fundamentals
from app.components import charts, alerts
from app.components import metrics as metrics_module

logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title=config.PAGE_TITLE,
    page_icon=config.PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data(ttl=int(config.CACHE_TTL.total_seconds()))
def load_ticker_data(symbol: str, period: str = config.DEFAULT_PERIOD, interval: str = config.DEFAULT_INTERVAL):
    return get_data(symbol, period=period, interval=interval, include_indicators=True)


@st.cache_data(ttl=int(config.CACHE_TTL.total_seconds()))
def load_multiple_watchlist(tickers_dict, period: str = config.DEFAULT_PERIOD, interval: str = config.DEFAULT_INTERVAL):
    return get_multiple_tickers(tickers_dict, period=period, interval=interval, include_indicators=True)


names = list(config.TICKERS.keys())
default_name = "Apple" if "Apple" in names else names[0]

st.sidebar.title("⚙️ Dashboard Settings")
selected_name = st.sidebar.selectbox("Asset", names, index=names.index(default_name))
selected_symbol = config.TICKERS[selected_name]
period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=3)
interval = st.sidebar.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)
compare_nse = st.sidebar.checkbox("Compare with NSE Index", value=True)
alert_threshold = st.sidebar.slider("Price alert threshold", 1.0, 15.0, 5.0, 0.5) / 100

st.sidebar.markdown("### 📋 Watchlist")
query_watchlist = st.query_params.get_all("watchlist") if hasattr(st.query_params, "get_all") else []
if "watchlist" not in st.session_state:
    st.session_state.watchlist = query_watchlist or ["Apple", "S&P 500", "Kenya Market Index (NSE20)"]

if st.sidebar.button("➕ Add selected asset"):
    if selected_name not in st.session_state.watchlist:
        st.session_state.watchlist.append(selected_name)
        st.query_params["watchlist"] = st.session_state.watchlist

remove_name = st.sidebar.selectbox("Remove asset", ["None"] + st.session_state.watchlist, index=0)
if st.sidebar.button("➖ Remove selected asset") and remove_name != "None":
    st.session_state.watchlist.remove(remove_name)
    st.query_params["watchlist"] = st.session_state.watchlist

if st.sidebar.button("🔄 Refresh market data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption("Current watchlist:")
st.sidebar.write(", ".join(st.session_state.watchlist))

st.title("📈 Global & Kenyan Market Dashboard")
st.caption("Live prices, technical indicators, comparative performance, and data exports. Research tool — not financial advice.")

with st.spinner(config.MESSAGES["loading"]):
    df = load_ticker_data(selected_symbol, period=period, interval=interval)

if df is None or df.empty:
    st.error(f"{config.MESSAGES['no_data']} for {selected_name} ({selected_symbol})")
    st.stop()

if "Date" in df.columns:
    df = df.set_index(pd.to_datetime(df["Date"]), drop=True)
elif not isinstance(df.index, pd.DatetimeIndex):
    df.index = pd.to_datetime(df.index, errors="coerce")

st.subheader(f"📊 {selected_name} ({selected_symbol})")
try:
    summary = metrics_module.get_summary_statistics(df)
except Exception as exc:
    logger.warning("metrics.get_summary_statistics failed", exc_info=exc)
    summary = {
        "Current_Price": float(df["Close"].iloc[-1]),
        "Change_Percent": float(((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100) if len(df) > 1 else 0,
        "Total_Return": float(((df["Close"].iloc[-1] / df["Close"].iloc[0]) - 1) * 100),
    }

col1, col2, col3, col4 = st.columns(4)
col1.metric("Price", f"{summary.get('Current_Price', 0):.2f}", delta=f"{summary.get('Change_Percent', 0):.2f}%")
col2.metric("24h Change", f"{summary.get('Change_Percent', 0):.2f}%")
col3.metric("Period Return", f"{summary.get('Total_Return', 0):.2f}%")
col4.metric("Volatility", f"{summary.get('Volatility', 0):.2f}" if summary.get("Volatility") is not None else "N/A")

overview_tab, price_tab, analysis_tab = st.tabs(["Overview", "Price & Volume", "Risk & Indicators"])

with overview_tab:
    fundamentals = get_fundamentals(selected_symbol)
    if fundamentals:
        left, right = st.columns(2)
        with left:
            st.markdown("**Company / Instrument**")
            st.write({k: v for k, v in fundamentals.items() if k in ("Name", "Sector", "Industry")})
        with right:
            st.markdown("**Valuation & Performance**")
            st.write({k: v for k, v in fundamentals.items() if k not in ("Name", "Sector", "Industry")})
    else:
        st.info("Fundamentals are not available for this instrument.")

with price_tab:
    st.plotly_chart(charts.plot_price_chart(df, f"{selected_name} ({selected_symbol})"), use_container_width=True)
    st.plotly_chart(charts.plot_volume_chart(df, f"{selected_name} ({selected_symbol})"), use_container_width=True)

with analysis_tab:
    st.plotly_chart(charts.plot_momentum_indicators(df, f"{selected_name} ({selected_symbol})"), use_container_width=True)

st.subheader("🚨 Alerts")
alert_list = alerts.generate_all_alerts(df, selected_name, price_threshold=alert_threshold)
if alert_list:
    for alert in alert_list:
        if alert.startswith("📈"):
            st.success(alert)
        elif alert.startswith("📉") or alert.startswith("⚠️"):
            st.error(alert)
        else:
            st.info(alert)
else:
    st.info("No alerts at this time.")

st.subheader("📋 Comparative Performance")
watchlist_dict = {name: config.TICKERS[name] for name in st.session_state.watchlist if name in config.TICKERS}
with st.spinner("Loading watchlist data..."):
    watchlist_data = load_multiple_watchlist(watchlist_dict, period=period, interval=interval)

if watchlist_data:
    st.plotly_chart(charts.plot_cumulative_returns(watchlist_data, "Cumulative Returns Comparison"), use_container_width=True)
else:
    st.info("No watchlist data available for comparison.")

if compare_nse:
    st.subheader("NSE vs Global Index Comparison")
    try:
        nse_df = load_ticker_data(config.TICKERS["Kenya Market Index (NSE20)"], period=period, interval=interval)
        sp_df = load_ticker_data(config.TICKERS["S&P 500"], period=period, interval=interval)
        if nse_df is not None and sp_df is not None and not nse_df.empty and not sp_df.empty:
            nse_df.index = pd.to_datetime(nse_df.index)
            sp_df.index = pd.to_datetime(sp_df.index)
            comparison = {
                "NSE20": nse_df[["Close"]].rename(columns={"Close": "Cumulative_Return"}).assign(
                    Cumulative_Return=lambda x: x["Cumulative_Return"].pct_change().fillna(0).add(1).cumprod().sub(1)
                ),
                "S&P 500": sp_df[["Close"]].rename(columns={"Close": "Cumulative_Return"}).assign(
                    Cumulative_Return=lambda x: x["Cumulative_Return"].pct_change().fillna(0).add(1).cumprod().sub(1)
                ),
            }
            st.plotly_chart(charts.plot_cumulative_returns(comparison, "NSE20 vs S&P 500 Cumulative Returns"), use_container_width=True)
        else:
            st.info("NSE or S&P 500 data is not available.")
    except Exception as exc:
        logger.error("Error loading index comparison", exc_info=exc)
        st.error("Failed to load the NSE or S&P 500 comparison.")

st.subheader("⬇️ Export")
export_data = df.reset_index().rename(columns={"index": "Date"})
st.download_button(
    "Download selected asset data as CSV",
    data=export_data.to_csv(index=False).encode("utf-8"),
    file_name=f"{selected_symbol.replace('^', '')}_{period}_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
)

st.markdown("---")
st.caption(f"Last updated: {datetime.now():%Y-%m-%d %H:%M:%S} | Data provided by Yahoo Finance")

with st.expander("Developer Panel"):
    st.write("Selected symbol:", selected_symbol)
    st.dataframe(df.tail().reset_index())
    st.write("Columns:", df.columns.tolist())






