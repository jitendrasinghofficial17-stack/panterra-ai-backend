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
        f"{BASE_URL}/prices/history",
        headers=headers,
        params={
            "ticker": symbol.upper(),
            "interval": "1day",
            "limit": 1
        },
        timeout=20
    )

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