from fastapi import APIRouter

from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators
from app.services.support_resistance import calculate_support_resistance

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

    if df is None or df.empty:
        return {
            "status": "error",
            "message": "Market data not available"
        }

    # Calculate indicators
    df = calculate_indicators(df)

    # Calculate support & resistance
    levels = calculate_support_resistance(df)

    latest = df.iloc[-1]

    signal = "HOLD"
    confidence = 55
    trend = "Sideways"
    reason = []

    if (
        latest["close"] > latest["EMA20"]
        and latest["EMA20"] > latest["SMA20"]
        and latest["RSI"] < 70
        and latest["MACD"] > latest["MACD_SIGNAL"]
    ):

        signal = "BUY"
        confidence = 90
        trend = "Bullish"

        reason = [
            "Price above EMA20",
            "EMA20 above SMA20",
            "RSI below 70",
            "MACD Bullish Crossover"
        ]

    elif (
        latest["close"] < latest["EMA20"]
        and latest["EMA20"] < latest["SMA20"]
        and latest["RSI"] > 30
        and latest["MACD"] < latest["MACD_SIGNAL"]
    ):

        signal = "SELL"
        confidence = 90
        trend = "Bearish"

        reason = [
            "Price below EMA20",
            "EMA20 below SMA20",
            "RSI above 30",
            "MACD Bearish Crossover"
        ]

    price = round(float(latest["close"]), 2)

    stop_loss = round(price * 0.98, 2)
    target = round(price * 1.05, 2)

    return {
        "symbol": symbol.upper(),
        "signal": signal,
        "trend": trend,
        "confidence": confidence,

        "price": price,
        "support": levels["support"],
        "resistance": levels["resistance"],

        "target": target,
        "stop_loss": stop_loss,

        "RSI": round(float(latest["RSI"]), 2),
        "EMA20": round(float(latest["EMA20"]), 2),
        "SMA20": round(float(latest["SMA20"]), 2),

        "MACD": round(float(latest["MACD"]), 4),
        "MACD_SIGNAL": round(float(latest["MACD_SIGNAL"]), 4),

        "reason": reason
    }