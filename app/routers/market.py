import os
import requests

from fastapi import APIRouter, HTTPException

router = APIRouter()

API_KEY = os.getenv("FINANCIALDATA_API_KEY")
BASE_URL = "https://api.financialdatasets.ai"


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

    headers = {
        "X-API-KEY": API_KEY
    }

    try:
        response = requests.get(
            f"{BASE_URL}/prices/snapshot",
            params={
                "ticker": symbol.upper()
            },
            headers=headers,
            timeout=20
        )

        # Debug logs
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

        if "prices" not in data or len(data["prices"]) == 0:
            raise HTTPException(
                status_code=404,
                detail="No market data found"
            )

        latest = data["prices"][-1]

        return {
            "symbol": symbol.upper(),
            "price": latest.get("close"),
            "open": latest.get("open"),
            "high": latest.get("high"),
            "low": latest.get("low"),
            "volume": latest.get("volume"),
            "date": latest.get("time")
        }

    except HTTPException:
        raise

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )