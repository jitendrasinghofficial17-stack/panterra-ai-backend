from datetime import datetime

from sqlalchemy.orm import Session

from app.models import TradeJournal
from app.schemas import (
    TradeJournalCreate,
    TradeJournalUpdate
)


def create_trade(
    db: Session,
    user_id: str,
    trade: TradeJournalCreate
):

    new_trade = TradeJournal(
        user_id=user_id,
        symbol=trade.symbol.upper(),
        trade_type=trade.trade_type.upper(),
        quantity=trade.quantity,
        entry_price=trade.entry_price,
        stop_loss=trade.stop_loss,
        target=trade.target,
        strategy=trade.strategy,
        notes=trade.notes,
        status="OPEN",
        pnl=0.0
    )

    db.add(new_trade)
    db.commit()
    db.refresh(new_trade)

    return new_trade


def get_all_trades(
    db: Session,
    user_id: str
):

    return (
        db.query(TradeJournal)
        .filter(
            TradeJournal.user_id == user_id
        )
        .order_by(
            TradeJournal.created_at.desc()
        )
        .all()
    )


def get_trade(
    db: Session,
    user_id: str,
    trade_id: int
):

    return (
        db.query(TradeJournal)
        .filter(
            TradeJournal.id == trade_id,
            TradeJournal.user_id == user_id
        )
        .first()
    )


def update_trade(
    db: Session,
    trade: TradeJournal,
    update: TradeJournalUpdate
):

    if update.exit_price is not None:
        trade.exit_price = update.exit_price

    if update.notes is not None:
        trade.notes = update.notes

    if update.status is not None:
        trade.status = update.status.upper()

    if update.pnl is not None:
        trade.pnl = update.pnl

    db.commit()
    db.refresh(trade)

    return trade


def close_trade(
    db: Session,
    trade: TradeJournal,
    exit_price: float
):

    trade.exit_price = exit_price

    if trade.trade_type == "BUY":

        trade.pnl = (
            exit_price -
            trade.entry_price
        ) * trade.quantity

    else:

        trade.pnl = (
            trade.entry_price -
            exit_price
        ) * trade.quantity

    trade.status = "CLOSED"

    trade.exit_time = datetime.utcnow()

    db.commit()
    db.refresh(trade)

    return trade


def delete_trade(
    db: Session,
    trade: TradeJournal
):

    db.delete(trade)
    db.commit()

    return {
        "status": "success",
        "message": "Trade deleted successfully"
    }