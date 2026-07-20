from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class TradeRequest(BaseModel):
    symbol: str
    trade_type: str
    entry_price: float
    current_price: float
    quantity: int
    atr: float


@router.get("/")
def home():
    return {
        "status": "success",
        "message": "AI Trade Manager Running"
    }


@router.post("/")
def manage_trade(data: TradeRequest):

    trade_type = data.trade_type.upper()

    entry = data.entry_price
    current = data.current_price
    qty = data.quantity
    atr = data.atr

    pnl = 0
    pnl_percent = 0

    initial_sl = 0
    trailing_sl = 0

    target1 = 0
    target2 = 0
    target3 = 0

    locked_profit = 0

    action = "HOLD"
    confidence = 90

    reason = []

    if trade_type == "BUY":

        pnl = (current - entry) * qty
        pnl_percent = ((current - entry) / entry) * 100

        initial_sl = round(entry - (1.5 * atr), 2)

        trailing_sl = max(
            initial_sl,
            round(current - (1.2 * atr), 2)
        )

        target1 = round(entry + (2 * atr), 2)
        target2 = round(entry + (3 * atr), 2)
        target3 = round(entry + (4 * atr), 2)

        locked_profit = max(
            0,
            round((trailing_sl - entry) * qty, 2)
        )

        if current >= target3:
            action = "BOOK FULL PROFIT"
            confidence = 99

            reason = [
                "Target 3 achieved",
                "Maximum reward reached"
            ]

        elif current >= target2:
            action = "BOOK 50% PROFIT"

            reason = [
                "Target 2 achieved",
                "Trail remaining quantity"
            ]

        elif current >= target1:
            action = "BOOK 25% PROFIT"

            reason = [
                "Target 1 achieved",
                "Move Stop Loss to Cost"
            ]

        else:

            action = "HOLD"

            reason = [
                "Trend still healthy"
            ]

    else:

        pnl = (entry - current) * qty
        pnl_percent = ((entry - current) / entry) * 100

        initial_sl = round(entry + (1.5 * atr), 2)

        trailing_sl = min(
            initial_sl,
            round(current + (1.2 * atr), 2)
        )

        target1 = round(entry - (2 * atr), 2)
        target2 = round(entry - (3 * atr), 2)
        target3 = round(entry - (4 * atr), 2)

        locked_profit = max(
            0,
            round((entry - trailing_sl) * qty, 2)
        )

        if current <= target3:

            action = "BOOK FULL PROFIT"

            confidence = 99

            reason = [
                "Target 3 achieved"
            ]

        elif current <= target2:

            action = "BOOK 50% PROFIT"

            reason = [
                "Target 2 achieved"
            ]

        elif current <= target1:

            action = "BOOK 25% PROFIT"

            reason = [
                "Target 1 achieved"
            ]

        else:

            action = "HOLD"

            reason = [
                "Trend still healthy"
            ]

    next_trailing_level = round(
        current + atr,
        2
    )

    return {

        "symbol": data.symbol.upper(),

        "trade_type": trade_type,

        "entry_price": entry,

        "current_price": current,

        "quantity": qty,

        "profit": round(pnl, 2),

        "profit_percent": round(pnl_percent, 2),

        "initial_stop_loss": initial_sl,

        "current_trailing_stop": trailing_sl,

        "locked_profit": locked_profit,

        "target1": target1,

        "target2": target2,

        "target3": target3,

        "next_trailing_level": next_trailing_level,

        "action": action,

        "confidence": confidence,

        "reason": reason
    }