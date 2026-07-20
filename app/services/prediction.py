import pandas as pd


def predict_price(df):

    latest = df.iloc[-1]

    price = float(latest["close"])

    ema20 = float(latest["EMA20"])
    sma20 = float(latest["SMA20"])

    rsi = float(latest["RSI"])

    macd = float(latest["MACD"])
    macd_signal = float(latest["MACD_SIGNAL"])

    atr = float(latest["ATR"])

    score = 0

    # Trend
    if price > ema20:
        score += 20

    if ema20 > sma20:
        score += 20

    # Momentum
    if macd > macd_signal:
        score += 20

    # RSI
    if 55 <= rsi <= 70:
        score += 20

    # Price action
    if latest["Supertrend_Direction"] == "BUY":
        score += 20

    confidence = score

    if confidence >= 80:
        prediction = "STRONG UP"

    elif confidence >= 60:
        prediction = "UP"

    elif confidence >= 40:
        prediction = "SIDEWAYS"

    else:
        prediction = "DOWN"

    tomorrow = round(price + atr * 0.5, 2)

    target3 = round(price + atr * 1.5, 2)

    target7 = round(price + atr * 3, 2)

    stop_loss = round(price - atr * 1.5, 2)

    return {
        "prediction": prediction,
        "confidence": confidence,
        "current_price": round(price, 2),
        "tomorrow_target": tomorrow,
        "three_day_target": target3,
        "seven_day_target": target7,
        "stop_loss": stop_loss
    }