from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import TradeJournal


def get_performance_summary(
    db: Session,
    user_id: str
):

    trades = (
        db.query(TradeJournal)
        .filter(
            TradeJournal.user_id == user_id
        )
        .all()
    )

    total_trades = len(trades)

    closed_trades = [
        t for t in trades
        if t.status == "CLOSED"
    ]

    open_trades = [
        t for t in trades
        if t.status == "OPEN"
    ]

    winning_trades = [
        t for t in closed_trades
        if t.pnl > 0
    ]

    losing_trades = [
        t for t in closed_trades
        if t.pnl < 0
    ]

    breakeven_trades = [
        t for t in closed_trades
        if t.pnl == 0
    ]

    gross_profit = sum(
        t.pnl
        for t in winning_trades
    )

    gross_loss = abs(
        sum(
            t.pnl
            for t in losing_trades
        )
    )

    net_profit = gross_profit - gross_loss

    win_rate = 0

    if len(closed_trades) > 0:
        win_rate = round(
            (
                len(winning_trades)
                / len(closed_trades)
            ) * 100,
            2
        )

    average_win = 0

    if winning_trades:
        average_win = round(
            gross_profit / len(winning_trades),
            2
        )

    average_loss = 0

    if losing_trades:
        average_loss = round(
            gross_loss / len(losing_trades),
            2
        )

    profit_factor = 0

    if gross_loss != 0:
        profit_factor = round(
            gross_profit / gross_loss,
            2
        )

    best_trade = 0

    if closed_trades:
        best_trade = max(
            t.pnl
            for t in closed_trades
        )

    worst_trade = 0

    if closed_trades:
        worst_trade = min(
            t.pnl
            for t in closed_trades
        )

    buy_trades = len([
        t for t in trades
        if t.trade_type == "BUY"
    ])

    sell_trades = len([
        t for t in trades
        if t.trade_type == "SELL"
    ])

    return {

        "status": "success",

        "summary": {

            "total_trades": total_trades,

            "closed_trades": len(closed_trades),

            "open_trades": len(open_trades),

            "winning_trades": len(winning_trades),

            "losing_trades": len(losing_trades),

            "breakeven_trades": len(breakeven_trades),

            "win_rate": win_rate,

            "gross_profit": round(
                gross_profit,
                2
            ),

            "gross_loss": round(
                gross_loss,
                2
            ),

            "net_profit": round(
                net_profit,
                2
            ),

            "average_win": average_win,

            "average_loss": average_loss,

            "profit_factor": profit_factor,

            "best_trade": round(
                best_trade,
                2
            ),

            "worst_trade": round(
                worst_trade,
                2
            ),

            "buy_trades": buy_trades,

            "sell_trades": sell_trades

        }

    }


def monthly_performance(
    db: Session,
    user_id: str
):

    trades = (
        db.query(TradeJournal)
        .filter(
            TradeJournal.user_id == user_id,
            TradeJournal.status == "CLOSED"
        )
        .all()
    )

    monthly = {}

    for trade in trades:

        month = trade.created_at.strftime("%Y-%m")

        if month not in monthly:

            monthly[month] = {
                "profit": 0,
                "trades": 0
            }

        monthly[month]["profit"] += trade.pnl
        monthly[month]["trades"] += 1

    return {

        "status": "success",

        "monthly": monthly

    }


def strategy_performance(
    db: Session,
    user_id: str
):

    trades = (
        db.query(TradeJournal)
        .filter(
            TradeJournal.user_id == user_id
        )
        .all()
    )

    result = {}

    for trade in trades:

        strategy = trade.strategy or "Unknown"

        if strategy not in result:

            result[strategy] = {

                "trades": 0,

                "profit": 0

            }

        result[strategy]["trades"] += 1

        result[strategy]["profit"] += trade.pnl

    return {

        "status": "success",

        "strategies": result

    }


def equity_curve(
    db: Session,
    user_id: str
):

    trades = (
        db.query(TradeJournal)
        .filter(
            TradeJournal.user_id == user_id,
            TradeJournal.status == "CLOSED"
        )
        .order_by(
            TradeJournal.created_at
        )
        .all()
    )

    equity = 0

    curve = []

    for trade in trades:

        equity += trade.pnl

        curve.append({

            "trade_id": trade.id,

            "symbol": trade.symbol,

            "equity": round(
                equity,
                2
            )

        })

    return {

        "status": "success",

        "equity_curve": curve

    }