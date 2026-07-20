from fastapi import APIRouter

from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators
from app.services.support_resistance import calculate_support_resistance
from app.services.atr import calculate_atr
from app.services.supertrend import calculate_supertrend

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

    # Calculate Indicators
    df = calculate_indicators(df)

    # Calculate ATR
    df = calculate_atr(df)

    # Calculate Supertrend
    df = calculate_supertrend(df)

    # Calculate Support & Resistance
    levels = calculate_support_resistance(df)

    latest = df.iloc[-1]

    signal = "HOLD"
    confidence = 55
    trend = "Sideways"
    reason = []

    supertrend = latest["Supertrend_Direction"]

    # STRONG BUY
    if (
        supertrend == "BUY"
        and latest["close"] > latest["EMA20"]
        and latest["EMA20"] > latest["SMA20"]
        and latest["RSI"] > 55
        and latest["RSI"] < 70
        and latest["MACD"] > latest["MACD_SIGNAL"]
    ):

        signal = "STRONG BUY"
        confidence = 97
        trend = "Bullish"

        reason = [
            "Supertrend BUY",
            "Price above EMA20",
            "EMA20 above SMA20",
            "MACD Bullish",
            "Healthy RSI"
        ]

    # STRONG SELL
    elif (
        supertrend == "SELL"
        and latest["close"] < latest["EMA20"]
        and latest["EMA20"] < latest["SMA20"]
        and latest["RSI"] < 45
        and latest["MACD"] < latest["MACD_SIGNAL"]
    ):

        signal = "STRONG SELL"
        confidence = 97
        trend = "Bearish"

        reason = [
            "Supertrend SELL",
            "Price below EMA20",
            "EMA20 below SMA20",
            "MACD Bearish",
            "Weak RSI"
        ]

    # BUY
    elif (
        latest["MACD"] > latest["MACD_SIGNAL"]
        and latest["RSI"] > 50
    ):

        signal = "BUY"
        confidence = 82
        trend = "Bullish"

        reason = [
            "MACD Bullish",
            "RSI Positive"
        ]

    # SELL
    elif (
        latest["MACD"] < latest["MACD_SIGNAL"]
        and latest["RSI"] < 50
    ):

        signal = "SELL"
        confidence = 82
        trend = "Bearish"

        reason = [
            "MACD Bearish",
            "RSI Weak"
        ]

    price = round(float(latest["close"]), 2)

    atr = round(float(latest["ATR"]), 2)

    stop_loss = round(price - (1.5 * atr), 2)

    target1 = round(price + (2 * atr), 2)
    target2 = round(price + (3 * atr), 2)
    target3 = round(price + (4 * atr), 2)

    risk = round(price - stop_loss, 2)
    reward = round(target2 - price, 2)

    if risk > 0:
        risk_reward = f"1:{round(reward / risk, 2)}"
    else:
        risk_reward = "N/A"

    return {
        "symbol": symbol.upper(),

        "signal": signal,
        "confidence": confidence,
        "trend": trend,

        "price": price,

        "support": levels["support"],
        "resistance": levels["resistance"],

        "supertrend": supertrend,
        "supertrend_value": round(float(latest["Supertrend"]), 2),

        "ATR": atr,

        "stop_loss": stop_loss,

        "target1": target1,
        "target2": target2,
        "target3": target3,

        "risk_reward": risk_reward,

        "RSI": round(float(latest["RSI"]), 2),
        "EMA20": round(float(latest["EMA20"]), 2),
        "SMA20": round(float(latest["SMA20"]), 2),

        "MACD": round(float(latest["MACD"]), 4),
        "MACD_SIGNAL": round(float(latest["MACD_SIGNAL"]), 4),

        "reason": reason
    }