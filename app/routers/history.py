import os
import requests

from fastapi import APIRouter, HTTPException

router = APIRouter()

API_KEY = os.getenv("FINANCIALDATA_API_KEY")
BASE_URL = "https://financialdata.net/api/v1"


@router.get("/{symbol}")
def get_history(symbol: str):

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
                "key": API_KEY,
                "limit": 200
            },
            timeout=20
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        return response.json()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )