import streamlit as st
from utils.data import fetch_ticker_data
from utils.strategies import build_stats_table, color_table

st.set_page_config(layout="wide", page_title="Backtest")
st.title("🔁 Strategy Backtest")

with st.form("backtest_form"):
    ticker_input = st.text_input("Enter ticker(s) separated by commas")
    submitted = st.form_submit_button("Run Backtest")

if submitted:
    tickers = [t.strip() for t in ticker_input.split(",")]
    for ticker in tickers:
        data = fetch_ticker_data(ticker,period="1y")
        close = data["Close"].dropna().squeeze()
        st.subheader(f"{ticker.upper()} — Strategy Comparison")
        stats_df = build_stats_table(close)
        st.dataframe(color_table(stats_df).format("{:.2f}"), use_container_width=True)
