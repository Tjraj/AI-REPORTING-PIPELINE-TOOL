import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_weather(city="New York", days=7):
    # Coordinates for common cities
    cities = {
        "New York": {"lat": 40.7128, "lon": -74.0060},
        "London": {"lat": 51.5074, "lon": -0.1278},
        "Mumbai": {"lat": 19.0760, "lon": 72.8777},
        "Delhi": {"lat": 28.6139, "lon": 77.2090},
        "Sydney": {"lat": -33.8688, "lon": 151.2093},
    }

    coords = cities.get(city, cities["New York"])

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
            "weathercode"
        ],
        "timezone": "auto",
        "forecast_days": days
    }

    response = requests.get(url, params=params)
    data = response.json()

    df = pd.DataFrame({
        "date": data["daily"]["time"],
        "temp_max": data["daily"]["temperature_2m_max"],
        "temp_min": data["daily"]["temperature_2m_min"],
        "precipitation": data["daily"]["precipitation_sum"],
        "windspeed": data["daily"]["windspeed_10m_max"],
        "weathercode": data["daily"]["weathercode"]
    })

    df["date"] = pd.to_datetime(df["date"])
    df["temp_avg"] = (df["temp_max"] + df["temp_min"]) / 2

    summary = {
        "city": city,
        "days": days,
        "avg_temp": round(df["temp_avg"].mean(), 1),
        "max_temp": round(df["temp_max"].max(), 1),
        "min_temp": round(df["temp_min"].min(), 1),
        "total_precipitation": round(df["precipitation"].sum(), 1),
        "avg_windspeed": round(df["windspeed"].mean(), 1),
        "rainy_days": int((df["precipitation"] > 1).sum()),
    }

    return df, summary