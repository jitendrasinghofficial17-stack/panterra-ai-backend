import math


def calculate_pcr(option_chain):
    """
    option_chain = {
        "calls": [
            {"strike":24000,"oi":120000,"change_oi":5000,"iv":14.2},
            ...
        ],
        "puts": [
            {"strike":24000,"oi":180000,"change_oi":9000,"iv":15.1},
            ...
        ]
    }
    """

    total_call_oi = sum(c.get("oi", 0) for c in option_chain["calls"])
    total_put_oi = sum(p.get("oi", 0) for p in option_chain["puts"])

    if total_call_oi == 0:
        pcr = 0
    else:
        pcr = round(total_put_oi / total_call_oi, 2)

    call_max = max(option_chain["calls"], key=lambda x: x.get("oi", 0))
    put_max = max(option_chain["puts"], key=lambda x: x.get("oi", 0))

    support = put_max["strike"]
    resistance = call_max["strike"]

    if pcr >= 1.30:
        outlook = "Strong Bullish"
        recommendation = "Buy Call"

    elif pcr >= 1.00:
        outlook = "Bullish"
        recommendation = "Bull Call Spread"

    elif pcr >= 0.80:
        outlook = "Neutral"
        recommendation = "Iron Condor"

    elif pcr >= 0.60:
        outlook = "Bearish"
        recommendation = "Buy Put"

    else:
        outlook = "Strong Bearish"
        recommendation = "Bear Put Spread"

    avg_iv = round(
        (
            sum(c.get("iv", 0) for c in option_chain["calls"])
            + sum(p.get("iv", 0) for p in option_chain["puts"])
        )
        /
        (
            len(option_chain["calls"])
            + len(option_chain["puts"])
        ),
        2
    )

    max_pain = round((support + resistance) / 2)

    confidence = min(
        95,
        round(abs(pcr - 1) * 100 + 65)
    )

    return {
        "put_call_ratio": pcr,
        "market_outlook": outlook,
        "recommended_strategy": recommendation,
        "support": support,
        "resistance": resistance,
        "max_pain": max_pain,
        "average_iv": avg_iv,
        "call_oi": total_call_oi,
        "put_oi": total_put_oi,
        "confidence": confidence,
        "highest_call_oi": call_max,
        "highest_put_oi": put_max
    }


def get_options_chain_ai(option_chain):
    return calculate_pcr(option_chain)