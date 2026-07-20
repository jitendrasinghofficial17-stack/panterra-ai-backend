import os
import requests
import pandas as pd

API_KEY = os.getenv("FINANCIALDATA_API_KEY")
BASE_URL = "https://financialdata.net/api/v1"


def get_historical_data(symbol, limit=200):

    try:

        response = requests.get(
            f"{BASE_URL}/stock-prices",
            params={
                "identifier": symbol.upper(),
                "limit": limit,
                "key": API_KEY
            },
            timeout=20
        )

        if response.status_code != 200:
            return None

        data = response.json()

        if not data:
            return None

        df = pd.DataFrame(data)

        df = df.rename(
            columns={
                "date": "date",
                "open": "open",
                "high": "high",
                "low": "low",
                "close": "close",
                "volume": "volume"
            }
        )

        df["date"] = pd.to_datetime(df["date"])

        df = df.sort_values("date")

        df.reset_index(drop=True, inplace=True)

        return df

    except Exception as e:
        print(e)
        return None