from fastapi import APIRouter
from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators

router = APIRouter()


@router.get("/")
def home():
    return {
        "status": "success",
        "message": "AI Signals API Running"
    }


@router.get("/{symbol}")
def get_signal(symbol: str):

    df = get_historical_data(symbol)

    if df is None:
        return {
            "status": "error",
            "message": "Market data not available"
        }

    df = calculate_indicators(df)

    latest = df.iloc[-1]

    signal = "HOLD"
    confidence = 55

    if (
        latest["close"] > latest["EMA20"]
        and latest["EMA20"] > latest["SMA20"]
        and latest["RSI"] < 70
        and latest["MACD"] > latest["MACD_SIGNAL"]
    ):
        signal = "BUY"
        confidence = 90

    elif (
        latest["close"] < latest["EMA20"]
        and latest["EMA20"] < latest["SMA20"]
        and latest["RSI"] > 30
        and latest["MACD"] < latest["MACD_SIGNAL"]
    ):
        signal = "SELL"
        confidence = 90

    return {
        "symbol": symbol.upper(),
        "signal": signal,
        "confidence": confidence,
        "price": round(float(latest["close"]), 2),
        "RSI": round(float(latest["RSI"]), 2),
        "EMA20": round(float(latest["EMA20"]), 2),
        "SMA20": round(float(latest["SMA20"]), 2),
        "MACD": round(float(latest["MACD"]), 2),
        "MACD_SIGNAL": round(float(latest["MACD_SIGNAL"]), 2),
    }