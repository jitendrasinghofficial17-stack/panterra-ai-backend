from fastapi import APIRouter

from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators
from app.services.atr import calculate_atr
from app.services.supertrend import calculate_supertrend
from app.services.adx import calculate_adx
from app.services.bollinger import calculate_bollinger_bands
from app.services.recommendation import generate_recommendation

router = APIRouter()


@router.get("/")
def home():
    return {
        "status": "success",
        "message": "AI Recommendation API Running"
    }


@router.get("/{symbol}")
def recommendation(symbol: str):

    try:
        df = get_historical_data(symbol)

        if df is None or df.empty:
            return {
                "status": "error",
                "message": "Market data not available"
            }

        # Calculate all indicators
        df = calculate_indicators(df)
        df = calculate_atr(df)
        df = calculate_supertrend(df)
        df = calculate_adx(df)
        df = calculate_bollinger_bands(df)

        # Generate recommendation
        result = generate_recommendation(df)

        return {
            "status": "success",
            "symbol": symbol.upper(),
            **result
        }

    except Exception as e:
        return {
            "status": "error",
            "symbol": symbol.upper(),
            "message": str(e)
        }