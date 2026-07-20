from app.models import TradeJournal


def analyze_trade(trade: TradeJournal):
    score = 100
    positives = []
    mistakes = []
    suggestions = []

    # ------------------------
    # Entry Analysis
    # ------------------------
    if trade.entry_price <= 0:
        score -= 20
        mistakes.append("Invalid entry price.")

    else:
        positives.append("Valid trade entry.")

    # ------------------------
    # Stop Loss Analysis
    # ------------------------
    if trade.stop_loss is None:
        score -= 15
        mistakes.append("Stop Loss not defined.")
        suggestions.append("Always place a Stop Loss before entering a trade.")

    else:
        positives.append("Stop Loss defined.")

    # ------------------------
    # Target Analysis
    # ------------------------
    if trade.target is None:
        score -= 10
        mistakes.append("Target not defined.")
        suggestions.append("Plan a profit target before taking a trade.")

    else:
        positives.append("Target planned.")

    # ------------------------
    # Risk Reward
    # ------------------------
    rr = None

    if (
        trade.stop_loss is not None
        and trade.target is not None
        and trade.entry_price is not None
    ):
        risk = abs(trade.entry_price - trade.stop_loss)
        reward = abs(trade.target - trade.entry_price)

        if risk > 0:
            rr = round(reward / risk, 2)

            if rr >= 2:
                positives.append(
                    f"Excellent Risk Reward ({rr}:1)"
                )
            elif rr >= 1:
                positives.append(
                    f"Acceptable Risk Reward ({rr}:1)"
                )
            else:
                score -= 10
                mistakes.append(
                    f"Poor Risk Reward ({rr}:1)"
                )
                suggestions.append(
                    "Aim for minimum 1:2 Risk Reward."
                )

    # ------------------------
    # Profit / Loss
    # ------------------------
    if trade.pnl > 0:
        positives.append(
            f"Profitable Trade (+{trade.pnl:.2f})"
        )
    elif trade.pnl < 0:
        score -= 10
        mistakes.append(
            f"Losing Trade ({trade.pnl:.2f})"
        )
        suggestions.append(
            "Review your entry timing and exit discipline."
        )

    # ------------------------
    # Strategy
    # ------------------------
    if trade.strategy:
        positives.append(
            f"Strategy Used: {trade.strategy}"
        )
    else:
        score -= 5
        mistakes.append("No trading strategy recorded.")

    # ------------------------
    # Notes
    # ------------------------
    if trade.notes:
        positives.append("Trade journal notes recorded.")
    else:
        suggestions.append(
            "Maintain detailed trade notes for future learning."
        )

    # ------------------------
    # Grade
    # ------------------------
    score = max(0, min(score, 100))

    if score >= 90:
        grade = "A+"

    elif score >= 80:
        grade = "A"

    elif score >= 70:
        grade = "B"

    elif score >= 60:
        grade = "C"

    elif score >= 50:
        grade = "D"

    else:
        grade = "F"

    return {
        "trade_id": trade.id,
        "symbol": trade.symbol,
        "score": score,
        "grade": grade,
        "status": trade.status,
        "pnl": trade.pnl,
        "risk_reward": rr,
        "positives": positives,
        "mistakes": mistakes,
        "suggestions": suggestions
    }