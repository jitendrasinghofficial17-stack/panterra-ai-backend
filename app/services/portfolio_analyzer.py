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


def analyze_portfolio(symbols: list[str]):

    holdings = []

    total_score = 0

    buy = 0
    hold = 0
    sell = 0

    for symbol in symbols:

        try:

            df = get_historical_data(symbol)

            if df is None or df.empty:
                continue

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

            total_score += ai["score"]

            if "BUY" in ai["action"]:
                buy += 1
            elif ai["action"] == "HOLD":
                hold += 1
            else:
                sell += 1

            holdings.append({

                "symbol": symbol,

                "price": round(float(latest["close"]), 2),

                "action": ai["action"],

                "grade": ai["grade"],

                "technical_score": ai["score"],

                "confidence": ai["confidence"],

                "trend": (
                    "Bullish"
                    if latest["EMA20"] > latest["SMA20"]
                    else "Bearish"
                ),

                "analysis": ai["reasons"]

            })

        except Exception as e:
            print(symbol, e)

    holdings.sort(
        key=lambda x: x["technical_score"],
        reverse=True
    )

    average_score = (
        round(total_score / len(holdings), 2)
        if holdings else 0
    )

    if average_score >= 90:
        health = "Excellent"
    elif average_score >= 75:
        health = "Strong"
    elif average_score >= 60:
        health = "Average"
    elif average_score >= 40:
        health = "Weak"
    else:
        health = "Poor"

    return {

        "status": "success",

        "portfolio_health": health,

        "average_score": average_score,

        "total_holdings": len(holdings),

        "buy_signals": buy,

        "hold_signals": hold,

        "sell_signals": sell,

        "best_stock": holdings[0] if holdings else None,

        "worst_stock": holdings[-1] if holdings else None,

        "holdings": holdings

    }