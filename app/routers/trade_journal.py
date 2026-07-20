from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models import User

from app.schemas import (
    TradeJournalCreate,
    TradeJournalUpdate
)

from app.services.trade_journal import (
    create_trade,
    get_all_trades,
    get_trade,
    update_trade,
    close_trade,
    delete_trade
)

router = APIRouter()


@router.get("/")
def home():
    return {
        "status": "success",
        "message": "Trade Journal API Working"
    }


@router.post("/create")
def add_trade(
    trade: TradeJournalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return create_trade(
        db,
        current_user.user_id,
        trade
    )


@router.get("/my")
def my_trades(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_all_trades(
        db,
        current_user.user_id
    )


@router.get("/{trade_id}")
def trade_details(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    trade = get_trade(
        db,
        current_user.user_id,
        trade_id
    )

    if trade is None:
        raise HTTPException(
            status_code=404,
            detail="Trade not found"
        )

    return trade


@router.put("/{trade_id}")
def edit_trade(
    trade_id: int,
    update: TradeJournalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    trade = get_trade(
        db,
        current_user.user_id,
        trade_id
    )

    if trade is None:
        raise HTTPException(
            status_code=404,
            detail="Trade not found"
        )

    return update_trade(
        db,
        trade,
        update
    )


@router.put("/{trade_id}/close")
def close_trade_position(
    trade_id: int,
    exit_price: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    trade = get_trade(
        db,
        current_user.user_id,
        trade_id
    )

    if trade is None:
        raise HTTPException(
            status_code=404,
            detail="Trade not found"
        )

    return close_trade(
        db,
        trade,
        exit_price
    )


@router.delete("/{trade_id}")
def remove_trade(
    trade_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    trade = get_trade(
        db,
        current_user.user_id,
        trade_id
    )

    if trade is None:
        raise HTTPException(
            status_code=404,
            detail="Trade not found"
        )

    return delete_trade(
        db,
        trade
    )