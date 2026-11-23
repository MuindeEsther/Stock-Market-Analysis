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

st.markdown("""
<style>
    :root { --text:#E5EEF7; --muted:#94A3B8; --cyan:#38BDF8; --green:#34D399; }
    .stApp { background:linear-gradient(135deg,#080E1A 0%,#0D1727 55%,#101D30 100%); color:var(--text); }
    section[data-testid="stSidebar"] { background:#0A1322; border-right:1px solid rgba(148,163,184,.12); }
    section[data-testid="stSidebar"] * { color:#DCE7F3; }
    .block-container { max-width:1440px; padding-top:1.25rem; padding-bottom:2rem; }
    h1,h2,h3,h4,p,span,label { color:var(--text); }
    [data-testid="stMetric"] { background:linear-gradient(145deg,#142238,#101B2E); border:1px solid rgba(148,163,184,.14); border-radius:14px; padding:18px 18px 14px; box-shadow:0 10px 28px rgba(0,0,0,.18); }
    [data-testid="stMetricLabel"] { color:var(--muted)!important; font-size:.78rem; text-transform:uppercase; letter-spacing:.06em; }
    [data-testid="stMetricValue"] { color:#F8FBFF!important; }
    [aria-selected="true"][data-testid="stTab"] { border-bottom-color:var(--cyan); color:var(--cyan); }
    [data-testid="stDataFrame"] { border:1px solid rgba(148,163,184,.12); border-radius:12px; overflow:hidden; }
    .stPlotlyChart { background:#101A2A; border:1px solid rgba(148,163,184,.12); border-radius:14px; padding:8px; box-shadow:0 12px 30px rgba(0,0,0,.16); }
    .hero { display:flex; justify-content:space-between; align-items:center; gap:16px; padding:22px 24px; margin-bottom:16px; border:1px solid rgba(56,189,248,.16); border-radius:18px; background:linear-gradient(120deg,rgba(56,189,248,.12),rgba(52,211,153,.05) 55%,rgba(17,28,46,.25)); box-shadow:0 18px 45px rgba(0,0,0,.18); }
    .hero h1 { margin:0; font-size:2rem; letter-spacing:-.03em; }
    .hero p { margin:.35rem 0 0; color:var(--muted); }
    .market-status { white-space:nowrap; border:1px solid rgba(52,211,153,.28); background:rgba(52,211,153,.08); color:#86EFAC; border-radius:999px; padding:.55rem .8rem; font-size:.78rem; font-weight:700; }
    .stDownloadButton button,.stButton button { border-radius:10px; border:1px solid rgba(56,189,248,.22); background:#122038; color:#E8F3FF; }
    [data-testid="stAlert"] { border-radius:12px; border:1px solid rgba(148,163,184,.12); }
</style>
""", unsafe_allow_html=True)

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
valid_query_watchlist = [name for name in query_watchlist if name in config.TICKERS]
if "watchlist" not in st.session_state:
    st.session_state.watchlist = valid_query_watchlist or ["Apple", "S&P 500", "Kenya Market Index (NSE20)"]

selected_watchlist = st.sidebar.multiselect(
    "Select watchlist assets",
    names,
    default=[name for name in st.session_state.watchlist if name in names],
    key="watchlist_multiselect",
)

if st.sidebar.button("💾 Save watchlist"):
    st.session_state.watchlist = list(selected_watchlist)
    st.query_params["watchlist"] = selected_watchlist
    st.success("Watchlist updated")

if st.sidebar.button("➕ Add selected asset"):
    if selected_name not in st.session_state.watchlist:
        st.session_state.watchlist.append(selected_name)
        st.query_params["watchlist"] = st.session_state.watchlist
        st.rerun()

remove_name = st.sidebar.selectbox("Remove asset", ["None"] + st.session_state.watchlist, index=0)
if st.sidebar.button("➖ Remove selected asset") and remove_name != "None":
    st.session_state.watchlist.remove(remove_name)
    st.query_params["watchlist"] = st.session_state.watchlist
    st.rerun()

if st.sidebar.button("🔄 Refresh market data"):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption("Current watchlist:")
st.sidebar.write(", ".join(st.session_state.watchlist))

st.markdown("""
<div class="hero">
  <div>
    <h1>Global & Kenyan Market Dashboard</h1>
    <p>Live prices · Technical intelligence · Comparative performance</p>
  </div>
  <div class="market-status">● DATA ONLINE</div>
</div>
""", unsafe_allow_html=True)

st.caption("Research tool — not financial advice.")

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
        def display_value(value, key=""):
            if value in (None, "N/A", ""):
                return "N/A"
            if key == "Market_Cap" and isinstance(value, (int, float)):
                return f"${value / 1_000_000_000:.2f}B"
            if key == "Dividend_Yield" and isinstance(value, (int, float)):
                return f"{value * 100:.2f}%"
            if isinstance(value, (int, float)):
                return f"{value:,.2f}" if key != "Dividend_Rate" else f"${value:,.2f}"
            return str(value)

        identity_col, valuation_col = st.columns([1, 1.35], gap="large")

        with identity_col:
            st.markdown("### Instrument Profile")
            profile_rows = [
                ("Name", fundamentals.get("Name")),
                ("Sector", fundamentals.get("Sector")),
                ("Industry", fundamentals.get("Industry")),
                ("Symbol", selected_symbol),
            ]
            for label, value in profile_rows:
                c1, c2 = st.columns([1, 2])
                c1.caption(label.upper())
                c2.markdown(f"**{display_value(value)}**")

        with valuation_col:
            st.markdown("### Key Fundamentals")
            card1, card2, card3 = st.columns(3)
            card1.metric("Market Cap", display_value(fundamentals.get("Market_Cap"), "Market_Cap"))
            card2.metric("P/E Ratio", display_value(fundamentals.get("PE_Ratio"), "PE_Ratio"))
            card3.metric("EPS", display_value(fundamentals.get("EPS"), "EPS"))

            fundamentals_table = pd.DataFrame([
                {"Metric": "Forward P/E", "Value": display_value(fundamentals.get("Forward_PE"), "Forward_PE")},
                {"Metric": "PEG Ratio", "Value": display_value(fundamentals.get("PEG_Ratio"), "PEG_Ratio")},
                {"Metric": "Price / Book", "Value": display_value(fundamentals.get("Price_to_Book"), "Price_to_Book")},
                {"Metric": "Dividend Yield", "Value": display_value(fundamentals.get("Dividend_Yield"), "Dividend_Yield")},
                {"Metric": "Beta", "Value": display_value(fundamentals.get("Beta"), "Beta")},
                {"Metric": "52-Week Range", "Value": f"{display_value(fundamentals.get('52_Week_Low'))} – {display_value(fundamentals.get('52_Week_High'))}"},
            ])
            st.dataframe(fundamentals_table, use_container_width=True, hide_index=True)
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






