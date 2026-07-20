from fastapi import APIRouter, HTTPException
import os
import requests
import pandas as pd

router = APIRouter()

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
            return None

        data = response.json()

        if not data:
            return None

        # Handle API response structure
        if isinstance(data, dict):
            if "data" in data:
                data = data["data"]
            elif "results" in data:
                data = data["results"]

        df = pd.DataFrame(data)

        if df.empty:
            return None

        required = ["date", "open", "high", "low", "close", "volume"]

        for col in required:
            if col not in df.columns:
                raise Exception(f"Missing column: {col}")

        df["date"] = pd.to_datetime(df["date"])

        df = df.sort_values("date")

        df.reset_index(drop=True, inplace=True)

        return df

    except Exception as e:
        print(e)
        return None


@router.get("/{symbol}")
def market(symbol: str):

    df = get_historical_data(symbol)

    if df is None:
        raise HTTPException(
            status_code=404,
            detail="Market data not found"
        )

    latest = df.iloc[-1]

    return {

        "symbol": symbol.upper(),

        "date": str(latest["date"]),

        "open": float(latest["open"]),

        "high": float(latest["high"]),

        "low": float(latest["low"]),

        "close": float(latest["close"]),

        "volume": float(latest["volume"])
    }