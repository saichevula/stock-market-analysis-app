import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import vectorbt as vbt
from utils.data import get_top5
from utils.strategies import build_stats_table  # if you moved it there

st.title("Stock Analysis")

with st.form("stock_form"):
    ticker_input = st.text_input("Enter ticker(s) separated by commas")
    submitted = st.form_submit_button("Submit")

if submitted:
    tickers = [t.strip() for t in ticker_input.split(",")]
    # your plotting and backtesting code here
    