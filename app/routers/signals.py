from fastapi import APIRouter
from app.services.market_data import get_historical_data
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

    df = get_historical_data(symbol)

    if df is None:
        return {
            "status": "error",
            "message": "Unable to fetch market data"
        }

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