import streamlit as st

st.set_page_config(layout="wide", page_title="Stock Analyzer")
st.title("📈 Stock Analyzer")

tab1, tab2 = st.tabs(["📈 Analysis", "🔁 Backtest"])

with tab1:
    import streamlit as st
    import numpy as np
    import plotly.graph_objects as go
    from utils.data import fetch_ticker_data

    st.set_page_config(layout="wide", page_title="Analysis")
    st.title("📈 Price Analysis")

    colors = ['#00b4d8', '#f72585', '#06d6a0']

    with st.form("stock_form"):
        ticker_input = st.text_input("Enter ticker(s) separated by commas")
        submitted = st.form_submit_button("Submit")

    if submitted:
        tickers = [t.strip() for t in ticker_input.split(",")]

    # --- Build all 3 charts across all tickers first ---
        fig_price = go.Figure()
        fig_ma = go.Figure()
        fig_returns = go.Figure()

        ticker_summaries = {}

        for i, ticker in enumerate(tickers):
            data = fetch_ticker_data(ticker,period="1y")
            if data.empty:
                st.warning(f"{ticker.upper()} is invalid.")
                continue

            close_data = data["Close"].dropna().squeeze()
            ma50 = close_data.rolling(window=50).mean()
            daily_return = close_data.pct_change() * 100

            fig_price.add_trace(go.Scatter(x=close_data.index, y=close_data, name=ticker.upper(), mode='lines'))
            fig_ma.add_trace(go.Scatter(x=ma50.index, y=ma50, name=ticker.upper(), mode='lines'))

            ticker_summaries[ticker.upper()] = {
                "best_day": data['Close'].idxmax().strftime("%b %d, %Y"),
                "worst_day": data['Close'].idxmin().strftime("%b %d, %Y"),
                "volatility": daily_return.std() * np.sqrt(252),
        }

        fig_price.update_layout(title="Closing Price", template="plotly_dark", xaxis_title="Date", yaxis_title="Price")
        fig_ma.update_layout(title="50-Day Moving Average", template="plotly_dark", xaxis_title="Date")

    # --- Side by side layout ---
        col_charts, col_summary = st.columns([2, 1])

        with col_charts:
            st.plotly_chart(fig_price, use_container_width=True)
            st.plotly_chart(fig_ma, use_container_width=True)

        with col_summary:
            for ticker, s in ticker_summaries.items():
                st.markdown(f"### {ticker} Summary")
                st.metric("Best Day", s["best_day"])
                st.metric("Worst Day", s["worst_day"])
                st.metric("Volatility (Annual)", f"{s['volatility']:.2f}%")
                st.divider()

with tab2:
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

    # paste your backtest page code here
