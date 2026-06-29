import vectorbt as vbt
import pandas as pd
import streamlit as st

def run_ma(close_data):
    fast = vbt.MA.run(close_data, 20)
    slow = vbt.MA.run(close_data, 50)
    entries = fast.ma_crossed_above(slow)
    exits = fast.ma_crossed_below(slow)
    return vbt.Portfolio.from_signals(close_data, entries, exits, init_cash=10_000, fees=0.001)

def run_rsi(close_data):
    rsi = vbt.RSI.run(close_data, window=14)
    entries = rsi.rsi < 30
    exits = rsi.rsi > 70
    return vbt.Portfolio.from_signals(close_data, entries, exits, init_cash=10_000, fees=0.001)

def run_bbands(close_data):
    bb = vbt.BBANDS.run(close_data, window=20, alpha=2)
    entries = close_data < bb.lower
    exits = close_data > bb.upper
    return vbt.Portfolio.from_signals(close_data, entries, exits, init_cash=10_000, fees=0.001)

def run_macd(close_data):
    macd = vbt.MACD.run(close_data, fast_window=12, slow_window=26, signal_window=9)
    entries = macd.macd.vbt.crossed_above(macd.signal)
    exits = macd.macd.vbt.crossed_below(macd.signal)
    return vbt.Portfolio.from_signals(close_data, entries, exits, init_cash=10_000, fees=0.001)

@st.cache_data
def build_stats_table(close_data):
    portfolios = {
        "MA Crossover": run_ma(close_data),
        "RSI": run_rsi(close_data),
        "Bollinger Bands": run_bbands(close_data),
        "MACD": run_macd(close_data),
    }
    metrics = ["Total Return [%]", "Max Drawdown [%]", "Win Rate [%]", "Profit Factor", "Expectancy", "Total Trades"]
    rows = {}
    for strategy_name, pf in portfolios.items():
        stats = pf.stats()
        rows[strategy_name] = {m: stats[m] for m in metrics if m in stats}
        rows[strategy_name]["Sharpe Ratio"] = round(pf.sharpe_ratio(freq='D'), 2)
    return pd.DataFrame(rows).round(2).T

def color_table(df):
    return df.style.highlight_max(axis=0, color="#1a7a4a")