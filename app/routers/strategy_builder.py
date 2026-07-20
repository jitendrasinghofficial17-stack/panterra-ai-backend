from fastapi import APIRouter, HTTPException

from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators
from app.services.atr import calculate_atr
from app.services.supertrend import calculate_supertrend
from app.services.volume import calculate_volume
from app.services.support_resistance import calculate_support_resistance
from app.services.candlestick import calculate_candlestick_patterns
from app.services.adx import calculate_adx
from app.services.bollinger import calculate_bollinger_bands

from app.services.strategy_builder import get_strategy

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "AI Strategy Builder API"
    }


@router.get("/{symbol}")
def strategy(symbol: str):

    df = get_historical_data(symbol)

    if df is None or df.empty:
        raise HTTPException(
            status_code=404,
            detail="No market data found"
        )

    df = calculate_indicators(df)
    df = calculate_atr(df)
    df = calculate_supertrend(df)
    df = calculate_volume(df)
    df = calculate_support_resistance(df)
    df = calculate_candlestick_patterns(df)
    df = calculate_adx(df)
    df = calculate_bollinger_bands(df)

    return get_strategy(df)