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

    response = requests.get(
        f"{BASE_URL}/prices/snapshot",
        params={"ticker": symbol.upper()},
        headers=headers,
        timeout=20
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail=response.text
        )

    return response.json()