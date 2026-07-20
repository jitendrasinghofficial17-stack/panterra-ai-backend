import os
import requests
import pandas as pd

API_KEY = os.getenv("FINANCIALDATA_API_KEY")


def get_historical_data(symbol: str):

    url = "https://api.financialdatasets.ai/prices/"

    headers = {
        "X-API-KEY": API_KEY
    }

    params = {
        "ticker": symbol.upper(),
        "interval": "day",
        "interval_multiplier": 1
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=20
        )

        if response.status_code != 200:
            print(response.text)
            return None

        data = response.json()

        prices = data.get("prices", [])

        if not prices:
            return None

        df = pd.DataFrame(prices)

        df["close"] = df["close"].astype(float)

        return df

    except Exception as e:
        print(e)
        return None