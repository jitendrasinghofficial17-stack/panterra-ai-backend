import pandas as pd


def calculate_ai_score(df):

    latest = df.iloc[-1]

    score = 0
    reasons = []

    # --------------------
    # TREND (20)
    # --------------------
    if latest["EMA20"] > latest["SMA20"]:
        score += 10
        reasons.append("EMA20 above SMA20")

    if latest["close"] > latest["EMA20"]:
        score += 10
        reasons.append("Price above EMA20")

    # --------------------
    # MOMENTUM (20)
    # --------------------
    if latest["MACD"] > latest["MACD_SIGNAL"]:
        score += 10
        reasons.append("MACD Bullish")

    if 50 <= latest["RSI"] <= 70:
        score += 10
        reasons.append("Healthy RSI")

    elif latest["RSI"] > 70:
        score -= 5
        reasons.append("Overbought")

    elif latest["RSI"] < 30:
        score += 5
        reasons.append("Oversold")

    # --------------------
    # ADX (10)
    # --------------------
    if latest["ADX"] >= 25:
        score += 10
        reasons.append("Strong Trend")

    # --------------------
    # SUPERTREND (10)
    # --------------------
    if latest["Supertrend_Direction"] == "BUY":
        score += 10
        reasons.append("Supertrend BUY")

    # --------------------
    # BOLLINGER (10)
    # --------------------
    if latest["BB_SIGNAL"] == "OVERSOLD":
        score += 10
        reasons.append("Near Lower Bollinger")

    elif latest["BB_SIGNAL"] == "OVERBOUGHT":
        score -= 5
        reasons.append("Near Upper Bollinger")

    # --------------------
    # VOLUME (10)
    # --------------------
    avg_volume = df["volume"].tail(20).mean()

    if latest["volume"] > avg_volume:
        score += 10
        reasons.append("High Volume")

    # --------------------
    # SIGNAL GRADE
    # --------------------
    if score >= 85:
        grade = "A+"

    elif score >= 75:
        grade = "A"

    elif score >= 65:
        grade = "B+"

    elif score >= 55:
        grade = "B"

    elif score >= 45:
        grade = "C"

    else:
        grade = "D"

    # --------------------
    # ACTION
    # --------------------
    if score >= 85:
        action = "STRONG BUY"

    elif score >= 70:
        action = "BUY"

    elif score >= 50:
        action = "HOLD"

    elif score >= 35:
        action = "SELL"

    else:
        action = "STRONG SELL"

    return {
        "score": score,
        "grade": grade,
        "action": action,
        "confidence": min(score, 100),
        "reasons": reasons
    }