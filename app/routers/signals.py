from fastapi import APIRouter
import pandas as pd
import random

from app.services.indicators import calculate_indicators

router = APIRouter()


@router.get("/")
def signals_home():
    return {
        "status": "success",
        "message": "AI Signals API Working"
    }


@router.get("/{symbol}")
def get_signal(symbol: str):

    # Temporary sample market data
    prices = []

    price = 100

    for _ in range(100):
        price += random.uniform(-2, 2)
        prices.append(price)

    df = pd.DataFrame({
        "close": prices
    })

    df = calculate_indicators(df)

    latest = df.iloc[-1]

    signal = "HOLD"

    if latest["RSI"] < 30:
        signal = "BUY"

    elif latest["RSI"] > 70:
        signal = "SELL"

    return {
        "symbol": symbol.upper(),
        "signal": signal,
        "price": round(float(latest["close"]), 2),
        "RSI": round(float(latest["RSI"]), 2),
        "EMA20": round(float(latest["EMA20"]), 2),
        "SMA20": round(float(latest["SMA20"]), 2),
        "MACD": round(float(latest["MACD"]), 2),
        "confidence": 70
    }