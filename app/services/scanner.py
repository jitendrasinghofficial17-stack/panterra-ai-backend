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

WATCHLIST = [
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


def scan_market():

    results = []

    for symbol in WATCHLIST:

        try:

            df = get_historical_data(symbol)

            if df is None or df.empty:
                continue

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

            # AI Engine
            ai = calculate_ai_score(df)

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

            # Support & Resistance (safe defaults)
            support = latest["Support"] if "Support" in latest.index else None
            resistance = latest["Resistance"] if "Resistance" in latest.index else None

            results.append({

                "symbol": symbol,

                "price": round(float(latest["close"]), 2),

                "action": ai["action"],

                "grade": ai["grade"],

                "technical_score": ai["score"],

                "confidence": ai["confidence"],

                "market_trend": market_trend,

                "trend_strength": trend_strength,

                "RSI": round(float(latest["RSI"]), 2),

                "ADX": round(float(latest["ADX"]), 2),

                "volume": int(latest["volume"]),

                "support": support,

                "resistance": resistance,

                "analysis": ai["reasons"]

            })

        except Exception as e:
            print(f"{symbol}: {e}")

    results = sorted(
        results,
        key=lambda x: x["technical_score"],
        reverse=True
    )

    for rank, stock in enumerate(results, start=1):
        stock["rank"] = rank

    return results