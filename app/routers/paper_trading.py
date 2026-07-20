from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models import User

from app.services.paper_trading import (
    place_buy_order,
    place_sell_order,
    get_orders,
    get_holdings,
    portfolio_summary,
    reset_account
)

router = APIRouter()


@router.get("/")
def home():

    return {
        "status": "success",
        "message": "Paper Trading API",
        "endpoints": [
            "/paper-trading/buy",
            "/paper-trading/sell",
            "/paper-trading/orders",
            "/paper-trading/holdings",
            "/paper-trading/summary",
            "/paper-trading/reset"
        ]
    }


@router.post("/buy")
def buy_stock(
    symbol: str,
    quantity: int,
    price: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return place_buy_order(
        db=db,
        user_id=current_user.user_id,
        symbol=symbol,
        quantity=quantity,
        price=price
    )


@router.post("/sell")
def sell_stock(
    symbol: str,
    quantity: int,
    price: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return place_sell_order(
        db=db,
        user_id=current_user.user_id,
        symbol=symbol,
        quantity=quantity,
        price=price
    )


@router.get("/orders")
def orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_orders(
        db,
        current_user.user_id
    )


@router.get("/holdings")
def holdings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_holdings(
        db,
        current_user.user_id
    )


@router.get("/summary")
def summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return portfolio_summary(
        db,
        current_user.user_id
    )


@router.delete("/reset")
def reset(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return reset_account(
        db,
        current_user.user_id
    )