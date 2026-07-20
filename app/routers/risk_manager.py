from fastapi import APIRouter
from pydantic import BaseModel

from app.services.risk_manager import calculate_position_size

router = APIRouter()


class PositionRequest(BaseModel):
    symbol: str
    capital: float
    risk_percent: float
    entry_price: float
    stop_loss: float


@router.get("/")
def home():
    return {
        "status": "success",
        "message": "AI Risk Manager Running"
    }


@router.post("/")
def calculate_position(data: PositionRequest):

    result = calculate_position_size(
        capital=data.capital,
        risk_percent=data.risk_percent,
        entry_price=data.entry_price,
        stop_loss=data.stop_loss
    )

    result["symbol"] = data.symbol.upper()

    return result