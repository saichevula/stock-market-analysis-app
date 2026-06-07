import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

# function to pull data and analyze it 
def plot_stock_data(ticker):
    fig, (ax_price,dx_ma,cx_return,tx) = plt.subplots(1,4, figsize=(14,5))
    summary=""
    for i in ticker:
        data = yf.Ticker(i.upper()).history(period="1y")
        if data.empty:
            print("Ticker is Invalid or doesn't Exist. Try again")
        else:
            close_data = data["Close"].dropna()
            ax_price.plot((close_data.index),(close_data), label=i.upper())


            final_moving_average = data['Close'].rolling(window=50).mean()
            dx_ma.plot((final_moving_average.index),(final_moving_average), label=i.upper())  

            data["Daily Return"] = close_data.pct_change() * 100
            annual_vol = data["Daily Return"].std() * np.sqrt(252)
            cx_return.plot(data.index, data["Daily Return"], label=i.upper(), alpha=0.5) 

            best_dayindex = data['Close'].idxmax().strftime("%B %d, %Y")
            worst_dayindex = data['Close'].idxmin().strftime("%B %d, %Y")

            summary += f"{i.upper()}\n"
            summary += f"Best Day: {best_dayindex}\n"
            summary += f"Worst Day: {worst_dayindex}\n"
            summary += f"Volatility: {annual_vol}\n\n"
    
    ax_price.set_xlabel("Date")
    ax_price.set_ylabel("Closing Price")
    ax_price.set_title("Closing Price")


    dx_ma.set_xlabel("Dates")
    dx_ma.set_ylabel("50 day Moving Average")
    dx_ma.set_title("50-Day Moving Average")


    cx_return.axhline(y=0, color="black", linestyle="--", linewidth=0.8)
    cx_return.set_xlabel("Date")
    cx_return.set_ylabel("Daily Return(%)")
    cx_return.set_title("Daily Returns")

    tx.text(0.05,0.95,summary,
        transform=tx.transAxes,
        verticalalignment='top',
        fontsize=10,
        fontfamily='monospace')
    tx.axis("off")
    tx.set_title("Summary")

    for ax_item in [ax_price, dx_ma, cx_return]:
        ax_item.tick_params(axis='x', rotation=45)
    ax_price.legend()
    dx_ma.legend()
    cx_return.legend()
    plt.show()

ticker = input("Enter ticker(with commas): ").split(",")
plot_stock_data(ticker)

    


        