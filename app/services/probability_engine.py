from app.services.option_scoring import option_scoring_service
from app.services.volatility_engine import volatility_engine


class ProbabilityEngine:

    def predict(self, contract: str):

        score = option_scoring_service.calculate_score(contract)
        volatility = volatility_engine.analyze(contract)

        if not score.get("available", False):
            return {
                "contract": contract,
                "available": False,
                "reason": "Option score unavailable"
            }

        if not volatility.get("available", False):
            return {
                "contract": contract,
                "available": False,
                "reason": "Volatility data unavailable"
            }

        final_score = score["final_score"]
        regime = volatility["volatility_regime"]
        iv = volatility["implied_volatility"]

        bullish = 50
        bearish = 50
        sideways = 20

        if final_score >= 90:
            bullish += 35
            bearish -= 25

        elif final_score >= 80:
            bullish += 25
            bearish -= 15

        elif final_score >= 70:
            bullish += 15
            bearish -= 10

        elif final_score <= 40:
            bearish += 30
            bullish -= 20

        if regime == "LOW":
            bullish += 5
            sideways += 5

        elif regime == "HIGH":
            bearish += 5
            sideways -= 5

        if iv > 60:
            breakout = 80

        elif iv > 40:
            breakout = 65

        else:
            breakout = 40

        reversal = max(
            10,
            100 - breakout
        )

        bullish = max(0, min(100, bullish))
        bearish = max(0, min(100, bearish))
        sideways = max(0, min(100, sideways))

        confidence = round(
            (final_score + volatility["volatility_score"]) / 2,
            2
        )

        if bullish > bearish:

            signal = "BULLISH"

        elif bearish > bullish:

            signal = "BEARISH"

        else:

            signal = "SIDEWAYS"

        return {

            "contract": contract,

            "available": True,

            "signal": signal,

            "confidence": confidence,

            "bullish_probability": bullish,

            "bearish_probability": bearish,

            "sideways_probability": sideways,

            "breakout_probability": breakout,

            "reversal_probability": reversal,

            "score": final_score,

            "volatility_score": volatility["volatility_score"],

            "grade": score["grade"]
        }


probability_engine = ProbabilityEngine()