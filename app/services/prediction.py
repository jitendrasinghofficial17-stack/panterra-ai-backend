import math


def predict_price(df):

    latest = df.iloc[-1]

    price = float(latest["close"])

    ema20 = float(latest["EMA20"])
    sma20 = float(latest["SMA20"])

    rsi = float(latest["RSI"])

    macd = float(latest["MACD"])
    macd_signal = float(latest["MACD_SIGNAL"])

    atr = float(latest["ATR"])

    adx = float(latest["ADX"])

    upper = float(latest["BB_UPPER"])
    lower = float(latest["BB_LOWER"])

    volume = float(latest["volume"])
    avg_volume = df["volume"].tail(20).mean()

    score = 0
    reasons = []

    # EMA Trend
    if price > ema20:
        score += 15
        reasons.append("Price above EMA20")

    if ema20 > sma20:
        score += 15
        reasons.append("EMA20 above SMA20")

    # MACD
    if macd > macd_signal:
        score += 15
        reasons.append("MACD Bullish")

    # RSI
    if 55 <= rsi <= 70:
        score += 15
        reasons.append("Healthy RSI")

    elif rsi > 70:
        score -= 10
        reasons.append("Overbought")

    elif rsi < 30:
        score += 10
        reasons.append("Oversold Bounce")

    # Supertrend
    if latest["Supertrend_Direction"] == "BUY":
        score += 15
        reasons.append("Supertrend BUY")

    # ADX
    if adx >= 25:
        score += 10
        reasons.append("Strong Trend")

    # Bollinger Bands
    if price < lower:
        score += 10
        reasons.append("Near Lower Bollinger")

    elif price > upper:
        score -= 10
        reasons.append("Near Upper Bollinger")

    # Relative Volume
    if volume > avg_volume:
        score += 5
        reasons.append("High Volume")

    confidence = max(0, min(score, 100))

    if confidence >= 85:
        prediction = "STRONG BUY"

    elif confidence >= 70:
        prediction = "BUY"

    elif confidence >= 50:
        prediction = "HOLD"

    elif confidence >= 30:
        prediction = "SELL"

    else:
        prediction = "STRONG SELL"

    target1 = round(price + atr, 2)
    target2 = round(price + atr * 2, 2)
    target3 = round(price + atr * 3, 2)

    stop = round(price - atr * 1.5, 2)

    rr = round((target2 - price) / (price - stop), 2)

    probability = min(95, confidence + math.floor(adx / 5))

    return {
        "prediction": prediction,
        "confidence": confidence,
        "success_probability": probability,
        "current_price": round(price, 2),
        "target1": target1,
        "target2": target2,
        "target3": target3,
        "stop_loss": stop,
        "risk_reward": f"1:{rr}",
        "reasons": reasons
    }