from app.services.option_scoring import option_scoring_service
from app.services.probability_engine import probability_engine
from app.services.market_regime import market_regime_service
from app.services.institutional_flow import institutional_flow_service
from app.services.volatility_engine import volatility_engine


class TradeRecommendationService:

    def analyze(self, symbol: str, contract: str):

        score = option_scoring_service.calculate_score(contract)
        probability = probability_engine.predict(contract)
        regime = market_regime_service.analyze(contract)
        flow = institutional_flow_service.analyze(symbol)
        volatility = volatility_engine.analyze(contract)

        services = [
            score,
            probability,
            regime,
            flow,
            volatility
        ]

        if not all(s.get("available", False) for s in services):
            return {
                "symbol": symbol,
                "contract": contract,
                "available": False,
                "reason": "Required analysis unavailable"
            }

        total_score = round(
            (
                score["final_score"] +
                probability["confidence"] +
                regime["market_score"] +
                flow["institutional_score"] +
                volatility["volatility_score"]
            ) / 5,
            2
        )

        if total_score >= 90:
            action = "STRONG BUY"

        elif total_score >= 80:
            action = "BUY"

        elif total_score >= 70:
            action = "ACCUMULATE"

        elif total_score >= 60:
            action = "HOLD"

        else:
            action = "EXIT"

        risk = "LOW"

        if volatility["implied_volatility"] > 50:
            risk = "HIGH"
        elif volatility["implied_volatility"] > 30:
            risk = "MEDIUM"

        return {

            "symbol": symbol,

            "contract": contract,

            "available": True,

            "trade_action": action,

            "overall_score": total_score,

            "market_regime": regime["market_regime"],

            "institutional_sentiment":
                flow["market_sentiment"],

            "probability_signal":
                probability["signal"],

            "confidence":
                probability["confidence"],

            "risk_level": risk,

            "recommendation":
                regime["recommendation"],

            "bullish_probability":
                probability["bullish_probability"],

            "bearish_probability":
                probability["bearish_probability"],

            "breakout_probability":
                probability["breakout_probability"],

            "reversal_probability":
                probability["reversal_probability"]
        }


trade_recommendation_service = TradeRecommendationService()