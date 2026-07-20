import os
import requests
import pandas as pd

API_KEY = os.getenv("FINANCIALDATA_API_KEY")

BASE_URL = "https://api.financialdatasets.ai"


def get_historical_data(symbol: str):

    headers = {
        "X-API-KEY": API_KEY
    }

    response = requests.get(
        f"{BASE_URL}/prices/history",
        headers=headers,
        params={
            "ticker": symbol.upper(),
            "interval": "1day",
            "limit": 100
        },
        timeout=20
    )

    if response.status_code != 200:
        print("API Error:", response.text)
        return None

    data = response.json()

    if "prices" not in data:
        print(data)
        return None

    df = pd.DataFrame(data["prices"])

    df["close"] = df["close"].astype(float)

    return df