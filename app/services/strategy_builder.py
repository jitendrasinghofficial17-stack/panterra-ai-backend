from app.services.ai_engine import calculate_ai_score


def generate_strategy(df):

    latest = df.iloc[-1]

    ai = calculate_ai_score(df)

    entry = []
    exit = []

    # EMA
    if latest["EMA20"] > latest["SMA20"]:
        entry.append("EMA20 above SMA20")
        exit.append("EMA20 crosses below SMA20")
    else:
        entry.append("EMA20 crosses above SMA20")
        exit.append("EMA20 below SMA20")

    # RSI
    if latest["RSI"] >= 55:
        entry.append("RSI above 55")
    else:
        entry.append("Wait for RSI above 55")

    exit.append("RSI below 45")

    # MACD
    if latest["MACD"] > latest["MACD_SIGNAL"]:
        entry.append("MACD Bullish Crossover")
    else:
        entry.append("Wait for MACD Bullish Crossover")

    exit.append("MACD Bearish Crossover")

    # Supertrend
    if latest["Supertrend_Direction"] == "BUY":
        entry.append("Supertrend BUY")
    else:
        entry.append("Wait for Supertrend BUY")

    exit.append("Supertrend SELL")

    # ADX
    if latest["ADX"] >= 25:
        entry.append("ADX above 25 confirms trend")
    else:
        entry.append("Wait for ADX above 25")

    atr = float(latest["ATR"])

    return {
        "strategy_name": "AI Momentum Strategy",

        "entry_rules": entry,

        "exit_rules": exit,

        "stop_loss": f"{round(atr * 1.5,2)} Points (ATR x1.5)",

        "target_1": f"{round(atr,2)} Points",

        "target_2": f"{round(atr*2,2)} Points",

        "target_3": f"{round(atr*3,2)} Points",

        "risk_reward": "1:2",

        "technical_score": ai["score"],

        "grade": ai["grade"],

        "confidence": ai["confidence"],

        "success_probability": min(
            ai["confidence"] + 5,
            95
        ),

        "signal": ai["action"],

        "analysis": ai["reasons"]
    }


def get_strategy(df):
    return generate_strategy(df)