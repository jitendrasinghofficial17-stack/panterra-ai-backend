from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators
from app.services.atr import calculate_atr
from app.services.supertrend import calculate_supertrend
from app.services.volume import calculate_volume
from app.services.support_resistance import calculate_support_resistance
from app.services.candlestick import calculate_candlestick_patterns
from app.services.adx import calculate_adx
from app.services.bollinger import calculate_bollinger_bands

from app.services.ai_engine import calculate_ai_score
from app.services.prediction import get_prediction
from app.services.recommendation import get_recommendation


def get_dashboard(symbol: str):

    df = get_historical_data(symbol)

    if df is None or df.empty:
        return {
            "status": "error",
            "message": "No market data found"
        }

    # Calculate Indicators
    df = calculate_indicators(df)
    df = calculate_atr(df)
    df = calculate_supertrend(df)
    df = calculate_volume(df)
    df = calculate_support_resistance(df)
    df = calculate_candlestick_patterns(df)
    df = calculate_adx(df)
    df = calculate_bollinger_bands(df)

    latest = df.iloc[-1]

    ai = calculate_ai_score(df)

    prediction = get_prediction(symbol)

    recommendation = get_recommendation(symbol)

    # Market Trend
    if latest["EMA20"] > latest["SMA20"]:
        market_trend = "Bullish"
    elif latest["EMA20"] < latest["SMA20"]:
        market_trend = "Bearish"
    else:
        market_trend = "Sideways"

    # Trend Strength
    if latest["ADX"] >= 40:
        trend_strength = "Very Strong"
    elif latest["ADX"] >= 25:
        trend_strength = "Strong"
    elif latest["ADX"] >= 20:
        trend_strength = "Moderate"
    else:
        trend_strength = "Weak"

    support = latest["Support"] if "Support" in latest.index else None
    resistance = latest["Resistance"] if "Resistance" in latest.index else None

    return {

        "status": "success",

        "symbol": symbol.upper(),

        "price": round(float(latest["close"]), 2),

        "market_trend": market_trend,

        "trend_strength": trend_strength,

        "technical_score": ai["score"],

        "grade": ai["grade"],

        "signal": ai["action"],

        "confidence": ai["confidence"],

        "prediction": prediction,

        "recommendation": recommendation,

        "support": support,

        "resistance": resistance,

        "indicators": {

            "EMA20": round(float(latest["EMA20"]), 2),

            "SMA20": round(float(latest["SMA20"]), 2),

            "RSI": round(float(latest["RSI"]), 2),

            "MACD": round(float(latest["MACD"]), 2),

            "MACD_SIGNAL": round(float(latest["MACD_SIGNAL"]), 2),

            "ATR": round(float(latest["ATR"]), 2),

            "ADX": round(float(latest["ADX"]), 2),

            "RVOL": round(float(latest["RVOL"]), 2),

            "Supertrend": latest["Supertrend_Direction"],

            "Bollinger": latest["BB_SIGNAL"],

            "Candlestick": latest["Candlestick"]

        },

        "analysis": ai["reasons"]

    }