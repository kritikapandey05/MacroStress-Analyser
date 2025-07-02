import yfinance as yf
import pandas as pd
from fredapi import Fred

def get_fred_series(series_id, api_key):
    fred = Fred(api_key=api_key)
    data = fred.get_series(series_id)
    return pd.DataFrame(data, columns=[series_id])

def get_market_data(ticker, start="2010-01-01", end="2024-12-31"):
    df = yf.download(ticker, start=start, end=end)[["Close"]]
    df = df.reset_index()
    df.columns = ["Date", "Price"]
    return df

def get_multiple_etfs(tickers, start="2010-01-01", end="2024-12-31"):
    df = yf.download(tickers, start=start, end=end)["Close"]
    df = df.reset_index()
    df = df.melt(id_vars=["Date"], var_name="ETF", value_name="Price")
    return df

def normalize_prices(df):
    df["Price"] = df.groupby("ETF")["Price"].transform(lambda x: (x / x.iloc[0]) * 100)
    return df
