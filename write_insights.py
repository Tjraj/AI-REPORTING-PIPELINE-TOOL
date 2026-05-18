content = """import json
import os
import time
import requests
import numpy as np
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

try:
    import streamlit as st
    API_KEY = st.secrets.get("GROQ_API_KEY") or os.getenv("GROQ_API_KEY")
except Exception:
    API_KEY = os.getenv("GROQ_API_KEY")

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
        "weather": "You are a meteorologist. Analyse: 1.Highlights 2.Extremes 3.Business impact 4.Recommendations. Data:",
        "stocks": "You are a financial analyst. Analyse: 1.Performance 2.Trends 3.Volume 4.Recommendations. Data:",
        "ecommerce": "You are an ecommerce analyst. Analyse: 1.Revenue 2.Categories 3.Insights 4.Recommendations. Data:"
    }
    prompt = prompt_map[source_type] + json.dumps(summary, cls=NumpyEncoder)
    headers = {
        "Authorization": "Bearer " + API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1024
    }
    for attempt in range(3):
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=body,
                timeout=60
            )
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            if "error" in data:
                msg = data["error"].get("message", str(data["error"]))
                code = data["error"].get("code", "")
                if code == 429 or "rate" in msg.lower():
                    time.sleep(5)
                    continue
                return "API Error: " + msg
            return "Unexpected: " + str(data)
        except Exception as e:
            if attempt < 2:
                time.sleep(3)
                continue
            return "Error: " + str(e)
    return "Failed after 3 attempts."
"""

with open("insights.py", "w") as f:
    f.write(content)
print("Done")