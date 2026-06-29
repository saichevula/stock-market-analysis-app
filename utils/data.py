import yfinance as yf
import pandas as pd

watchlist = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "BRK-B"]

def fetch_ticker_data(ticker, period="1y"):
    data = yf.Ticker(ticker.upper()).history(period=period)
    return data

def get_top5():
    prices = {}
    for ticker in watchlist:
        data = yf.Ticker(ticker).history(period="1d")
        if not data.empty:
            prices[ticker] = round(data['Close'].iloc[-1], 2)
    top5 = sorted(prices, key=prices.get, reverse=True)[:5]
    return pd.DataFrame({
        "Ticker": top5,
        "Price": [f"${prices[t]}" for t in top5]
    })