from app.services.option_chain_service import option_chain_service
from app.services.option_scoring import option_scoring_service
from app.services.volatility_engine import volatility_engine


class InstitutionalFlowService:

    def analyze(self, symbol: str):

        chain = option_chain_service.get_chain(symbol)

        if not chain:

            return {
                "symbol": symbol,
                "available": False,
                "reason": "Option chain unavailable"
            }

        calls = option_chain_service.filter_calls(chain)
        puts = option_chain_service.filter_puts(chain)

        call_oi = 0
        put_oi = 0

        call_volume = 0
        put_volume = 0

        highest_call = None
        highest_put = None

        max_call_oi = 0
        max_put_oi = 0

        for item in calls:

            oi = float(item.get("open_interest", 0))
            volume = float(item.get("volume", 0))

            call_oi += oi
            call_volume += volume

            if oi > max_call_oi:
                max_call_oi = oi
                highest_call = item

        for item in puts:

            oi = float(item.get("open_interest", 0))
            volume = float(item.get("volume", 0))

            put_oi += oi
            put_volume += volume

            if oi > max_put_oi:
                max_put_oi = oi
                highest_put = item

        pcr = round(
            put_oi / call_oi,
            2
        ) if call_oi else 0

        if pcr > 1.2:
            sentiment = "BULLISH"

        elif pcr < 0.8:
            sentiment = "BEARISH"

        else:
            sentiment = "NEUTRAL"

        score = 50

        if sentiment == "BULLISH":
            score += 25

        elif sentiment == "BEARISH":
            score += 20

        if put_volume > call_volume:
            score += 10

        score = min(score, 100)

        recommendation = "WAIT"

        if sentiment == "BULLISH":
            recommendation = "BUY CALL"

        elif sentiment == "BEARISH":
            recommendation = "BUY PUT"

        confidence = min(score + 5, 95)

        return {

            "symbol": symbol,

            "available": True,

            "market_sentiment": sentiment,

            "institutional_score": score,

            "confidence": confidence,

            "recommendation": recommendation,

            "put_call_ratio": pcr,

            "total_call_open_interest": call_oi,

            "total_put_open_interest": put_oi,

            "total_call_volume": call_volume,

            "total_put_volume": put_volume,

            "highest_call_oi": highest_call,

            "highest_put_oi": highest_put
        }

    def analyze_contract(self, contract: str):

        score = option_scoring_service.calculate_score(contract)
        volatility = volatility_engine.analyze(contract)

        if not score.get("available", False):

            return {
                "contract": contract,
                "available": False
            }

        flow_score = (
            score["final_score"] +
            volatility["volatility_score"]
        ) / 2

        if flow_score >= 90:
            flow = "STRONG BUY"

        elif flow_score >= 80:
            flow = "BUY"

        elif flow_score >= 70:
            flow = "ACCUMULATE"

        elif flow_score >= 60:
            flow = "HOLD"

        else:
            flow = "EXIT"

        return {

            "contract": contract,

            "available": True,

            "institutional_flow_score": round(flow_score, 2),

            "institutional_signal": flow,

            "confidence": round(
                (
                    score["confidence"] +
                    volatility["confidence"]
                ) / 2,
                2
            ),

            "price_score": score["price_score"],

            "greeks_score": score["greeks_score"],

            "volatility_score": volatility["volatility_score"]
        }


institutional_flow_service = InstitutionalFlowService()