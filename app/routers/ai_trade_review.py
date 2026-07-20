from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import TradeJournal
from app.services.ai_trade_review import analyze_trade

router = APIRouter(
    prefix="/ai-trade-review",
    tags=["AI Trade Review"]
)


@router.get("/")
def home():
    return {
        "message": "AI Trade Review API"
    }


@router.get("/{trade_id}")
def review_trade(
    trade_id: int,
    db: Session = Depends(get_db)
):
    trade = (
        db.query(TradeJournal)
        .filter(TradeJournal.id == trade_id)
        .first()
    )

    if not trade:
        raise HTTPException(
            status_code=404,
            detail="Trade not found"
        )

    return analyze_trade(trade)


@router.get("/user/{user_id}")
def review_all_trades(
    user_id: str,
    db: Session = Depends(get_db)
):
    trades = (
        db.query(TradeJournal)
        .filter(TradeJournal.user_id == user_id)
        .all()
    )

    reviews = [
        analyze_trade(trade)
        for trade in trades
    ]

    return {
        "user_id": user_id,
        "total_trades": len(reviews),
        "reviews": reviews
    }