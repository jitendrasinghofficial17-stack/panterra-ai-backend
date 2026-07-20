from sqlalchemy.orm import Session
from app.models import PaperTrade

INITIAL_BALANCE = 1000000.0


def get_cash_balance(db: Session, user_id: str):

    trades = (
        db.query(PaperTrade)
        .filter(PaperTrade.user_id == user_id)
        .all()
    )

    balance = INITIAL_BALANCE

    for trade in trades:

        amount = trade.price * trade.quantity

        if trade.order_type == "BUY":
            balance -= amount

        elif trade.order_type == "SELL":
            balance += amount

    return round(balance, 2)


def place_buy_order(
    db: Session,
    user_id: str,
    symbol: str,
    quantity: int,
    price: float
):

    balance = get_cash_balance(db, user_id)

    cost = quantity * price

    if cost > balance:

        return {
            "status": "failed",
            "message": "Insufficient balance"
        }

    order = PaperTrade(
        user_id=user_id,
        symbol=symbol.upper(),
        order_type="BUY",
        quantity=quantity,
        price=price,
        status="EXECUTED"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "status": "success",
        "order": order,
        "remaining_balance": get_cash_balance(db, user_id)
    }


def place_sell_order(
    db: Session,
    user_id: str,
    symbol: str,
    quantity: int,
    price: float
):

    holdings = get_holdings(db, user_id)

    if symbol.upper() not in holdings:

        return {
            "status": "failed",
            "message": "No Holdings"
        }

    if holdings[symbol.upper()]["quantity"] < quantity:

        return {
            "status": "failed",
            "message": "Not enough shares"
        }

    order = PaperTrade(
        user_id=user_id,
        symbol=symbol.upper(),
        order_type="SELL",
        quantity=quantity,
        price=price,
        status="EXECUTED"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return {
        "status": "success",
        "order": order,
        "remaining_balance": get_cash_balance(db, user_id)
    }


def get_orders(
    db: Session,
    user_id: str
):

    return (
        db.query(PaperTrade)
        .filter(PaperTrade.user_id == user_id)
        .order_by(PaperTrade.created_at.desc())
        .all()
    )


def get_holdings(
    db: Session,
    user_id: str
):

    trades = (
        db.query(PaperTrade)
        .filter(PaperTrade.user_id == user_id)
        .all()
    )

    portfolio = {}

    for trade in trades:

        symbol = trade.symbol

        if symbol not in portfolio:

            portfolio[symbol] = {
                "quantity": 0,
                "investment": 0
            }

        if trade.order_type == "BUY":

            portfolio[symbol]["quantity"] += trade.quantity
            portfolio[symbol]["investment"] += (
                trade.quantity * trade.price
            )

        else:

            portfolio[symbol]["quantity"] -= trade.quantity
            portfolio[symbol]["investment"] -= (
                trade.quantity * trade.price
            )

    portfolio = {
        k: v
        for k, v in portfolio.items()
        if v["quantity"] > 0
    }

    return portfolio


def portfolio_summary(
    db: Session,
    user_id: str
):

    holdings = get_holdings(db, user_id)

    invested = sum(
        h["investment"]
        for h in holdings.values()
    )

    return {

        "cash_balance": get_cash_balance(
            db,
            user_id
        ),

        "invested_amount": round(
            invested,
            2
        ),

        "number_of_holdings": len(
            holdings
        ),

        "holdings": holdings
    }


def reset_account(
    db: Session,
    user_id: str
):

    db.query(PaperTrade).filter(
        PaperTrade.user_id == user_id
    ).delete()

    db.commit()

    return {

        "status": "success",

        "message": "Paper Trading account reset successfully",

        "balance": INITIAL_BALANCE

    }