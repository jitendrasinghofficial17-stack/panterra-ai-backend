from fastapi import APIRouter

from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators
from app.services.atr import calculate_atr
from app.services.supertrend import calculate_supertrend
from app.services.adx import calculate_adx
from app.services.bollinger import calculate_bollinger_bands
from app.services.ai_engine import calculate_ai_score

router = APIRouter()

# You can expand this list later
SYMBOLS = [
    "AAPL",
    "MSFT",
    "NVDA",
    "AMZN",
    "META",
    "GOOGL",
    "TSLA",
    "NFLX",
    "AMD",
    "PLTR"
]


@router.get("/")
def scanner():

    results = []

    for symbol in SYMBOLS:

        try:

            df = get_historical_data(symbol)

            if df is None or df.empty:
                continue

            df = calculate_indicators(df)
            df = calculate_atr(df)
            df = calculate_supertrend(df)
            df = calculate_adx(df)
            df = calculate_bollinger_bands(df)

            ai = calculate_ai_score(df)

            latest = df.iloc[-1]

            results.append({

                "symbol": symbol,

                "price": round(float(latest["close"]), 2),

                "action": ai["action"],

                "grade": ai["grade"],

                "score": ai["score"],

                "confidence": ai["confidence"],

                "trend": (
                    "Bullish"
                    if latest["EMA20"] > latest["SMA20"]
                    else "Bearish"
                )

            })

        except Exception:
            continue

    results = sorted(
        results,
        key=lambda x: x["score"],
        reverse=True
    )

    for index, stock in enumerate(results, start=1):
        stock["rank"] = index

    return {
        "status": "success",
        "market": "US",
        "total_stocks": len(results),
        "stocks": results
    }