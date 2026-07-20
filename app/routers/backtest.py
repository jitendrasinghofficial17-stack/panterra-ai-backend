from fastapi import APIRouter
from app.services.backtest import backtest

router = APIRouter()


@router.get("/{symbol}")
def run_backtest(symbol: str):

    trades = backtest(symbol)

    if trades is None:
        return {
            "status": "error"
        }

    total = len(trades)

    wins = len([x for x in trades if x > 0])

    losses = total - wins

    net_profit = round(sum(trades), 2)

    win_rate = round((wins / total) * 100, 2) if total else 0

    return {

        "symbol": symbol.upper(),

        "total_trades": total,

        "wins": wins,

        "losses": losses,

        "win_rate": win_rate,

        "net_profit": net_profit
    }