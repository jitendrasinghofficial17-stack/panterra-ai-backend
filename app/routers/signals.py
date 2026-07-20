from fastapi import APIRouter

from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators
from app.services.atr import calculate_atr
from app.services.supertrend import calculate_supertrend
from app.services.volume import calculate_volume
from app.services.support_resistance import calculate_support_resistance
from app.services.candlestick import calculate_candlestick_patterns
from app.services.adx import calculate_adx

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

    # Technical Indicators
    df = calculate_indicators(df)
    df = calculate_atr(df)
    df = calculate_supertrend(df)
    df = calculate_volume(df)
    df = calculate_candlestick_patterns(df)
    df = calculate_adx(df)

    # Support & Resistance
    levels = calculate_support_resistance(df)

    latest = df.iloc[-1]

    supertrend = latest["Supertrend_Direction"]
    candlestick = latest["Candlestick"]

    adx = round(float(latest["ADX"]), 2)
    plus_di = round(float(latest["PLUS_DI"]), 2)
    minus_di = round(float(latest["MINUS_DI"]), 2)

    signal = "HOLD"
    confidence = 50
    trend = "Sideways"
    reason = []

    # ===============================
    # STRONG BUY
    # ===============================
    if (
        supertrend == "BUY"
        and latest["close"] > latest["EMA20"]
        and latest["EMA20"] > latest["SMA20"]
        and latest["MACD"] > latest["MACD_SIGNAL"]
        and 55 <= latest["RSI"] <= 70
        and latest["RVOL"] >= 1
        and latest["ADX"] >= 25
        and candlestick in [
            "HAMMER",
            "BULLISH_ENGULFING",
            "BULLISH_HARAMI"
        ]
    ):

        signal = "STRONG BUY"
        confidence = 99
        trend = "Bullish"

        reason = [
            "Supertrend BUY",
            "Strong ADX",
            "EMA Bullish",
            "MACD Bullish",
            "Healthy RSI",
            "Strong Volume",
            candlestick
        ]

    # ===============================
    # STRONG SELL
    # ===============================
    elif (
        supertrend == "SELL"
        and latest["close"] < latest["EMA20"]
        and latest["EMA20"] < latest["SMA20"]
        and latest["MACD"] < latest["MACD_SIGNAL"]
        and latest["RSI"] < 45
        and latest["RVOL"] >= 1
        and latest["ADX"] >= 25
        and candlestick in [
            "SHOOTING_STAR",
            "BEARISH_ENGULFING",
            "BEARISH_HARAMI"
        ]
    ):

        signal = "STRONG SELL"
        confidence = 99
        trend = "Bearish"

        reason = [
            "Supertrend SELL",
            "Strong ADX",
            "EMA Bearish",
            "MACD Bearish",
            "Weak RSI",
            "Strong Volume",
            candlestick
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

    risk_reward = (
        f"1:{round(reward / risk,2)}"
        if risk > 0 else "N/A"
    )

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

        "candlestick": candlestick,

        "ADX": adx,
        "PLUS_DI": plus_di,
        "MINUS_DI": minus_di,

        "ATR": atr,

        "stop_loss": stop_loss,

        "target1": target1,
        "target2": target2,
        "target3": target3,

        "risk_reward": risk_reward,

        "volume": int(latest["volume"]),
        "volume_ma20": round(float(latest["Volume_MA20"]), 0),
        "rvol": round(float(latest["RVOL"]), 2),
        "volume_signal": latest["Volume_Signal"],

        "RSI": round(float(latest["RSI"]), 2),
        "EMA20": round(float(latest["EMA20"]), 2),
        "SMA20": round(float(latest["SMA20"]), 2),

        "MACD": round(float(latest["MACD"]), 4),
        "MACD_SIGNAL": round(float(latest["MACD_SIGNAL"]), 4),

        "reason": reason
    }