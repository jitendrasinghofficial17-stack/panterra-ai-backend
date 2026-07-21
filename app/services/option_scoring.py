from app.services.option_price_service import option_price_service
from app.services.option_greeks_service import option_greeks_service


class OptionScoringService:

    def calculate_score(self, contract: str):

        price = option_price_service.analyze(contract)
        greeks = option_greeks_service.analyze(contract)

        if not price.get("available", False):
            return {
                "contract": contract,
                "available": False,
                "reason": "Price data unavailable"
            }

        if not greeks.get("available", False):
            return {
                "contract": contract,
                "available": False,
                "reason": "Greeks data unavailable"
            }

        price_score = price.get("price_score", 0)
        greeks_score = greeks.get("greeks_score", 0)

        final_score = round(
            (price_score * 0.50) +
            (greeks_score * 0.50),
            2
        )

        confidence = round(
            (price_score + greeks_score) / 2,
            2
        )

        trend = price.get("trend", "UNKNOWN")
        volume = price.get("volume_signal", "NORMAL")
        delta = greeks.get("delta", 0)
        iv = greeks.get("implied_volatility", 0)

        if final_score >= 90:
            grade = "A+"
            signal = "STRONG BUY"

        elif final_score >= 80:
            grade = "A"
            signal = "BUY"

        elif final_score >= 70:
            grade = "B"
            signal = "ACCUMULATE"

        elif final_score >= 60:
            grade = "C"
            signal = "HOLD"

        else:
            grade = "D"
            signal = "AVOID"

        strengths = []

        if trend in ["BREAKOUT", "BULLISH"]:
            strengths.append("Bullish Trend")

        if volume == "HIGH":
            strengths.append("High Volume")

        if abs(delta) >= 0.60:
            strengths.append("Strong Delta")

        if iv < 30:
            strengths.append("Low Implied Volatility")

        risks = []

        if trend == "BEARISH":
            risks.append("Bearish Trend")

        if volume == "LOW":
            risks.append("Weak Volume")

        if iv > 60:
            risks.append("High Implied Volatility")

        if greeks.get("theta", 0) < -0.10:
            risks.append("High Time Decay")

        return {

            "contract": contract,

            "available": True,

            "price_score": price_score,

            "greeks_score": greeks_score,

            "final_score": final_score,

            "grade": grade,

            "signal": signal,

            "confidence": confidence,

            "trend": trend,

            "volume_signal": volume,

            "delta": delta,

            "implied_volatility": iv,

            "strengths": strengths,

            "risks": risks,

            "price_analysis": price,

            "greeks_analysis": greeks
        }

    def rank_contracts(self, contracts):

        ranked = []

        for contract in contracts:

            try:

                result = self.calculate_score(contract)

                if result.get("available", False):
                    ranked.append(result)

            except Exception:
                continue

        ranked.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return ranked


option_scoring_service = OptionScoringService()