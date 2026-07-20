import os
import requests

from fastapi import APIRouter, HTTPException

router = APIRouter()

API_KEY = os.getenv("FINANCIALDATA_API_KEY")
BASE_URL = "https://financialdata.net/api/v1"


@router.get("/")
def market_home():
    return {
        "status": "success",
        "message": "Live Market API Working"
    }


@router.get("/quote/{symbol}")
def get_quote(symbol: str):

    if not API_KEY:
        raise HTTPException(
            status_code=500,
            detail="FINANCIALDATA_API_KEY not configured"
        )

    try:
        response = requests.get(
            f"{BASE_URL}/stock-prices",
            params={
                "identifier": symbol.upper(),
                "key": API_KEY
            },
            timeout=20
        )

        print("========== FINANCIAL DATA API ==========")
        print("URL:", response.url)
        print("Status:", response.status_code)
        print("Response:", response.text)
        print("========================================")

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        data = response.json()

        if not data:
            raise HTTPException(
                status_code=404,
                detail="No market data found"
            )

        latest = data[0]

        return {
            "symbol": latest.get("trading_symbol", symbol.upper()),
            "price": latest.get("close"),
            "open": latest.get("open"),
            "high": latest.get("high"),
            "low": latest.get("low"),
            "volume": latest.get("volume"),
            "date": latest.get("date")
        }

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )