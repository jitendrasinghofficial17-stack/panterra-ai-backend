from app.services.ai_engine import calculate_ai_score


def generate_recommendation(df):

    ai = calculate_ai_score(df)

    latest = df.iloc[-1]

    price = float(latest["close"])
    atr = float(latest["ATR"])

    # Entry Zone
    entry = round(price, 2)
    buy_zone_low = round(price - atr * 0.30, 2)
    buy_zone_high = round(price + atr * 0.30, 2)

    # Targets
    target1 = round(price + atr, 2)
    target2 = round(price + atr * 2, 2)
    target3 = round(price + atr * 3, 2)

    # Stop Loss
    stop_loss = round(price - atr * 1.5, 2)

    # Risk Reward
    risk = price - stop_loss
    reward = target2 - price

    rr = round(reward / risk, 2) if risk > 0 else 0

    # Market Trend
    if latest["EMA20"] > latest["SMA20"]:
        market_trend = "Bullish"

    elif latest["EMA20"] < latest["SMA20"]:
        market_trend = "Bearish"

    else:
        market_trend = "Sideways"

    # Trend Strength
    adx = float(latest["ADX"])

    if adx >= 40:
        trend_strength = "Very Strong"

    elif adx >= 25:
        trend_strength = "Strong"

    elif adx >= 20:
        trend_strength = "Moderate"

    else:
        trend_strength = "Weak"

    # Risk Level
    if rr >= 3:
        risk_level = "LOW"

    elif rr >= 2:
        risk_level = "MEDIUM"

    else:
        risk_level = "HIGH"

    return {

        "market_trend": market_trend,

        "action": ai["action"],

        "signal_quality": ai["grade"],

        "confidence": ai["confidence"],

        "success_probability": min(
            ai["confidence"] + 5,
            95
        ),

        "entry": {
            "ideal": entry,
            "buy_zone_low": buy_zone_low,
            "buy_zone_high": buy_zone_high
        },

        "targets": {
            "target1": target1,
            "target2": target2,
            "target3": target3
        },

        "stop_loss": stop_loss,

        "holding_period": "3-7 Days",

        "trend_strength": trend_strength,

        "risk": {
            "level": risk_level,
            "risk_reward": f"1:{rr}"
        },

        "technical_score": ai["score"],

        "analysis": ai["reasons"]
    }