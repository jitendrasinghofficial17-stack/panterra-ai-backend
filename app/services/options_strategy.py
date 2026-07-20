def generate_options_strategy(df):

    latest = df.iloc[-1]

    rsi = float(latest["RSI"])
    adx = float(latest["ADX"])
    atr = float(latest["ATR"])
    signal = latest["Supertrend_Direction"]

    if signal == "BUY" and rsi > 55:
        strategy = "Buy Call (Long CE)"
        outlook = "Bullish"

    elif signal == "SELL" and rsi < 45:
        strategy = "Buy Put (Long PE)"
        outlook = "Bearish"

    elif adx < 20:
        strategy = "Short Straddle / Iron Fly"
        outlook = "Range Bound"

    else:
        strategy = "Iron Condor"
        outlook = "Neutral"

    return {
        "market_outlook": outlook,
        "recommended_strategy": strategy,
        "entry_signal": signal,
        "atr": round(atr, 2),
        "risk": "Medium",
        "holding_period": "Intraday / 1-3 Days"
    }


def get_options_strategy(df):
    return generate_options_strategy(df)