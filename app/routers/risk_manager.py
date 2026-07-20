from math import floor


def calculate_position_size(
    capital: float,
    risk_percent: float,
    entry_price: float,
    stop_loss: float,
    min_rr: float = 3.0
):

    risk_amount = capital * (risk_percent / 100)

    risk_per_share = abs(entry_price - stop_loss)

    if risk_per_share <= 0:
        return {
            "error": "Invalid Stop Loss"
        }

    quantity = floor(risk_amount / risk_per_share)

    capital_required = round(quantity * entry_price, 2)

    remaining_cash = round(capital - capital_required, 2)

    target_price = round(
        entry_price + (risk_per_share * min_rr),
        2
    )

    expected_profit = round(
        (target_price - entry_price) * quantity,
        2
    )

    maximum_loss = round(
        risk_per_share * quantity,
        2
    )

    return {

        "capital": capital,

        "risk_percent": risk_percent,

        "risk_amount": round(risk_amount, 2),

        "entry_price": entry_price,

        "stop_loss": stop_loss,

        "risk_per_share": round(risk_per_share, 2),

        "recommended_quantity": quantity,

        "capital_required": capital_required,

        "remaining_cash": remaining_cash,

        "target_price": target_price,

        "expected_profit": expected_profit,

        "maximum_loss": maximum_loss,

        "risk_reward": f"1:{min_rr}"
    }