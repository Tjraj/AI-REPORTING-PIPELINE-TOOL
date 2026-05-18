import json
import os
import time
import requests
import numpy as np
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

try:
    import streamlit as st
    API_KEY = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")
except Exception:
    API_KEY = os.getenv("OPENROUTER_API_KEY")


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        if isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)


def generate_insights(source_type, summary):
    prompt_map = {
        "weather": "You are a senior meteorologist. Analyse this weather data and provide: 1. Key highlights 2. Extreme conditions 3. Business impact 4. Three recommendations.\n\nData:\n",
        "stocks": "You are a senior financial analyst. Analyse this stock data and provide: 1. Price performance 2. Trend observations 3. Volume analysis 4. Three recommendations.\n\nData:\n",
        "ecommerce": "You are a senior ecommerce analyst. Analyse this store data and provide: 1. Revenue highlights 2. Best and worst categories 3. Customer insights 4. Three recommendations.\n\nData:\n"
    }

    prompt = prompt_map[source_type] + json.dumps(summary, indent=2, cls=NumpyEncoder)

    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:8501",
        "X-Title": "AI Reporting Pipeline"
    }

    body = {
        "model": "deepseek/deepseek-v4-flash:free",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 1024
    }

    for attempt in range(3):
        try:
            r = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=body,
                timeout=60
            )
            data = r.json()

            if "choices" in data:
                return data["choices"][0]["message"]["content"]

            if "error" in data:
                err = data["error"]
                code = err.get("code", "")
                msg = err.get("message", str(err))

                if code == 401 or "auth" in msg.lower():
                    return "AUTH FAILED: Key wrong or expired. Get fresh key from openrouter.ai"

                if code == 429 or "rate" in msg.lower():
                    time.sleep(5)
                    continue

                if "model" in msg.lower():
                    body["model"] = "mistralai/mistral-7b-instruct:free"
                    continue

                return "API Error " + str(code) + ": " + msg

            return "Unexpected response: " + json.dumps(data)

        except requests.exceptions.ConnectionError:
            if attempt < 2:
                time.sleep(3)
                continue
            return "Connection failed. Check internet."

        except requests.exceptions.Timeout:
            if attempt < 2:
                time.sleep(3)
                continue
            return "Request timed out after 3 attempts."

        except Exception as e:
            return "Error: " + str(e)

    return "Failed after 3 attempts. Try again."