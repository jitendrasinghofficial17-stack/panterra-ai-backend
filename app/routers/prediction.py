from fastapi import APIRouter

from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators
from app.services.atr import calculate_atr
from app.services.supertrend import calculate_supertrend
from app.services.prediction import predict_price

router = APIRouter()


@router.get("/")
def home():
    return {
        "status": "success",
        "message": "AI Prediction API Running"
    }


@router.get("/{symbol}")
def prediction(symbol: str):

    df = get_historical_data(symbol)

    if df is None or df.empty:
        return {
            "status": "error",
            "message": "Market data not available"
        }

    df = calculate_indicators(df)
    df = calculate_atr(df)
    df = calculate_supertrend(df)

    result = predict_price(df)

    return {
        "symbol": symbol.upper(),
        **result
    }