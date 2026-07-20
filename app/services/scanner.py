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

            signal = "HOLD"

            if (
                latest["Supertrend_Direction"] == "BUY"
                and latest["MACD"] > latest["MACD_SIGNAL"]
                and latest["RSI"] > 50
            ):
                signal = "BUY"

            elif (
                latest["Supertrend_Direction"] == "SELL"
                and latest["MACD"] < latest["MACD_SIGNAL"]
                and latest["RSI"] < 50
            ):
                signal = "SELL"

            results.append({

                "symbol": symbol,

                "price": round(float(latest["close"]),2),

                "signal": signal,

                "trend": latest["Supertrend_Direction"],

                "RSI": round(float(latest["RSI"]),2),

                "ADX": round(float(latest["ADX"]),2)

            })

        except Exception as e:
            print(e)

    return results