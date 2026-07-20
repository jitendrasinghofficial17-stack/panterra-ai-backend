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

DEFAULT_SYMBOLS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "META",
    "GOOGL",
    "AMZN",
    "TSLA",
    "NFLX",
    "AMD",
    "PLTR"
]


def scan_market(
    symbols=None,
    min_score=0,
    action=None,
    limit=50
):

    if symbols is None:
        symbols = DEFAULT_SYMBOLS

    results = []

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

            trend = (
                "Bullish"
                if latest["EMA20"] > latest["SMA20"]
                else "Bearish"
            )

            trend_strength = (
                "Very Strong"
                if latest["ADX"] >= 40
                else "Strong"
                if latest["ADX"] >= 25
                else "Moderate"
                if latest["ADX"] >= 20
                else "Weak"
            )

            stock = {

                "symbol": symbol,

                "price": round(float(latest["close"]), 2),

                "action": ai["action"],

                "grade": ai["grade"],

                "technical_score": ai["score"],

                "confidence": ai["confidence"],

                "trend": trend,

                "trend_strength": trend_strength,

                "RSI": round(float(latest["RSI"]), 2),

                "ADX": round(float(latest["ADX"]), 2),

                "ATR": round(float(latest["ATR"]), 2),

                "volume": int(latest["volume"]),

                "analysis": ai["reasons"]

            }

            if stock["technical_score"] < min_score:
                continue

            if action and stock["action"] != action:
                continue

            results.append(stock)

        except Exception as e:
            print(symbol, e)

    results.sort(
        key=lambda x: x["technical_score"],
        reverse=True
    )

    for i, stock in enumerate(results, start=1):
        stock["rank"] = i

    return {
        "status": "success",
        "total": len(results[:limit]),
        "stocks": results[:limit]
    }