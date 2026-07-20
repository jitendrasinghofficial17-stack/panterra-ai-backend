from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators
from app.services.atr import calculate_atr
from app.services.supertrend import calculate_supertrend
from app.services.volume import calculate_volume
from app.services.support_resistance import calculate_support_resistance
from app.services.candlestick import calculate_candlestick_patterns
from app.services.adx import calculate_adx
from app.services.bollinger import calculate_bollinger_bands

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

            df = calculate_indicators(df)
            df = calculate_atr(df)
            df = calculate_supertrend(df)
            df = calculate_volume(df)
            df = calculate_candlestick_patterns(df)
            df = calculate_adx(df)
            df = calculate_bollinger_bands(df)

            latest = df.iloc[-1]

            score = 0
            reasons = []

            # -------------------------
            # Supertrend
            # -------------------------
            if latest["Supertrend_Direction"] == "BUY":
                score += 20
                reasons.append("Supertrend BUY")

            # -------------------------
            # RSI
            # -------------------------
            if 55 <= latest["RSI"] <= 70:
                score += 15
                reasons.append("Healthy RSI")

            elif latest["RSI"] > 70:
                score += 8
                reasons.append("Strong Momentum")

            # -------------------------
            # MACD
            # -------------------------
            if latest["MACD"] > latest["MACD_SIGNAL"]:
                score += 15
                reasons.append("MACD Bullish")

            # -------------------------
            # EMA
            # -------------------------
            if latest["close"] > latest["EMA20"]:
                score += 10
                reasons.append("Above EMA20")

            # -------------------------
            # SMA
            # -------------------------
            if latest["EMA20"] > latest["SMA20"]:
                score += 10
                reasons.append("EMA > SMA")

            # -------------------------
            # ADX
            # -------------------------
            if latest["ADX"] >= 25:
                score += 10
                reasons.append("Strong Trend")

            # -------------------------
            # Relative Volume
            # -------------------------
            if latest["RVOL"] >= 1:
                score += 10
                reasons.append("High Volume")

            # -------------------------
            # Bollinger
            # -------------------------
            if latest["BB_SIGNAL"] == "NORMAL":
                score += 5

            # -------------------------
            # Candlestick
            # -------------------------
            if latest["Candlestick"] in [
                "HAMMER",
                "BULLISH_ENGULFING",
                "BULLISH_HARAMI"
            ]:
                score += 10
                reasons.append(latest["Candlestick"])

            # -------------------------
            # Final Signal
            # -------------------------
            if score >= 90:
                signal = "STRONG BUY"

            elif score >= 75:
                signal = "BUY"

            elif score >= 60:
                signal = "WATCH"

            elif score >= 40:
                signal = "HOLD"

            else:
                signal = "SELL"

            results.append({

                "symbol": symbol,

                "price": round(float(latest["close"]), 2),

                "signal": signal,

                "score": score,

                "confidence": score,

                "trend": latest["Supertrend_Direction"],

                "RSI": round(float(latest["RSI"]), 2),

                "ADX": round(float(latest["ADX"]), 2),

                "volume": int(latest["volume"]),

                "reason": reasons

            })

        except Exception as e:
            print(symbol, e)

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    return results