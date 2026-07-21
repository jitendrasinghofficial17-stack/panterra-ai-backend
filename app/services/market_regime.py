from app.services.option_scoring import option_scoring_service
from app.services.volatility_engine import volatility_engine
from app.services.probability_engine import probability_engine


class MarketRegimeService:

    def analyze(self, contract: str):

        score = option_scoring_service.calculate_score(contract)
        volatility = volatility_engine.analyze(contract)
        probability = probability_engine.predict(contract)

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
                "reason": "Volatility unavailable"
            }

        if not probability.get("available", False):
            return {
                "contract": contract,
                "available": False,
                "reason": "Probability unavailable"
            }

        trend = score.get("trend", "UNKNOWN")
        volume = score.get("volume_signal", "NORMAL")
        signal = probability.get("signal", "SIDEWAYS")

        hv = volatility.get("historical_volatility", 0)
        iv = volatility.get("implied_volatility", 0)

        regime = "SIDEWAYS"

        if signal == "BULLISH" and trend in ["BULLISH", "BREAKOUT"]:

            regime = "BULL MARKET"

        elif signal == "BEARISH" and trend in ["BEARISH", "BREAKDOWN"]:

            regime = "BEAR MARKET"

        elif iv > 60:

            regime = "HIGH VOLATILITY"

        elif hv < 15:

            regime = "LOW VOLATILITY"

        elif volume == "HIGH":

            regime = "TRENDING"

        confidence = round(
            (
                score["confidence"] +
                volatility["confidence"] +
                probability["confidence"]
            ) / 3,
            2
        )

        score_value = round(
            (
                score["final_score"] +
                volatility["volatility_score"]
            ) / 2,
            2
        )

        if regime == "BULL MARKET":

            recommendation = "BUY CALL"

        elif regime == "BEAR MARKET":

            recommendation = "BUY PUT"

        elif regime == "HIGH VOLATILITY":

            recommendation = "OPTION SELLING"

        elif regime == "LOW VOLATILITY":

            recommendation = "LONG STRADDLE"

        else:

            recommendation = "WAIT"

        return {

            "contract": contract,

            "available": True,

            "market_regime": regime,

            "recommendation": recommendation,

            "confidence": confidence,

            "market_score": score_value,

            "trend": trend,

            "signal": signal,

            "volume_signal": volume,

            "historical_volatility": hv,

            "implied_volatility": iv,

            "bullish_probability":
                probability["bullish_probability"],

            "bearish_probability":
                probability["bearish_probability"],

            "sideways_probability":
                probability["sideways_probability"],

            "breakout_probability":
                probability["breakout_probability"],

            "reversal_probability":
                probability["reversal_probability"]
        }


market_regime_service = MarketRegimeService()