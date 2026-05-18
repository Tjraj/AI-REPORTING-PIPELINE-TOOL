import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_stocks(symbol="IBM", days=30):
    api_key = os.getenv("ALPHA_VANTAGE_KEY")

    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": api_key,
        "outputsize": "compact"
    }

    response = requests.get(url, params=params)
    data = response.json()

    if "Time Series (Daily)" not in data:
        # Fallback mock data if API limit hit
        import numpy as np
        dates = pd.date_range(end=pd.Timestamp.today(), periods=days)
        base = 150
        prices = [base + i * 0.5 + (i % 3) * 2 for i in range(days)]
        df = pd.DataFrame({
            "date": dates,
            "close": prices,
            "open": [p - 1 for p in prices],
            "high": [p + 2 for p in prices],
            "low": [p - 2 for p in prices],
            "volume": [1000000 + i * 5000 for i in range(days)]
        })
    else:
        ts = data["Time Series (Daily)"]
        records = []
        for date, values in list(ts.items())[:days]:
            records.append({
                "date": date,
                "open": float(values["1. open"]),
                "high": float(values["2. high"]),
                "low": float(values["3. low"]),
                "close": float(values["4. close"]),
                "volume": int(values["5. volume"])
            })
        df = pd.DataFrame(records)
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date")

    df["daily_change"] = df["close"].pct_change() * 100
    df["ma7"] = df["close"].rolling(7).mean()

    summary = {
        "symbol": symbol,
        "latest_close": round(df["close"].iloc[-1], 2),
        "open_price": round(df["open"].iloc[-1], 2),
        "period_high": round(df["high"].max(), 2),
        "period_low": round(df["low"].min(), 2),
        "avg_volume": int(df["volume"].mean()),
        "price_change_pct": round(df["daily_change"].iloc[-1], 2),
        "days_analysed": len(df)
    }

    return df, summary