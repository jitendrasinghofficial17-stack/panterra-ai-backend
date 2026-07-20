import os
import requests
import pandas as pd

API_KEY = os.getenv("FINANCIALDATA_API_KEY")

BASE_URL = "https://financialdata.net/api/v1"


def get_historical_data(symbol: str, limit: int = 200):

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
            print(response.text)
            return None

        data = response.json()

        if isinstance(data, dict):
            if "data" in data:
                data = data["data"]
            elif "results" in data:
                data = data["results"]

        if not data:
            return None

        df = pd.DataFrame(data)

        required_columns = [
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]

        for col in required_columns:
            if col not in df.columns:
                return None

        df["date"] = pd.to_datetime(df["date"])

        numeric_cols = [
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col])

        df = df.sort_values("date")

        df.reset_index(drop=True, inplace=True)

        return df

    except Exception as e:
        print(e)
        return None