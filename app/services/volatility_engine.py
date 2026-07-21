from math import sqrt
from statistics import mean, stdev

from app.services.option_price_service import option_price_service
from app.services.option_greeks_service import option_greeks_service


class VolatilityEngine:

    TRADING_DAYS = 252

    def historical_volatility(self, closes):

        if len(closes) < 2:
            return 0

        returns = []

        for i in range(1, len(closes)):

            previous = closes[i - 1]

            if previous == 0:
                continue

            returns.append(
                (closes[i] - previous) / previous
            )

        if len(returns) < 2:
            return 0

        return round(
            stdev(returns) * sqrt(self.TRADING_DAYS) * 100,
            2
        )

    def atr(self, highs, lows, closes):

        if len(closes) < 2:
            return 0

        tr = []

        for i in range(1, len(closes)):

            tr1 = highs[i] - lows[i]

            tr2 = abs(highs[i] - closes[i - 1])

            tr3 = abs(lows[i] - closes[i - 1])

            tr.append(max(tr1, tr2, tr3))

        if not tr:
            return 0

        return round(mean(tr), 2)

    def expected_move(self, price, iv, days=1):

        if price == 0 or iv == 0:
            return 0

        move = price * (iv / 100) * sqrt(days / 365)

        return round(move, 2)

    def volatility_regime(self, hv, iv):

        if hv == 0 and iv == 0:
            return "UNKNOWN"

        if iv > hv + 10:
            return "HIGH"

        if iv < hv - 10:
            return "LOW"

        return "NORMAL"

    def analyze(self, contract):

        history = option_price_service.get_prices(contract)

        if not history:

            return {
                "contract": contract,
                "available": False
            }

        closes = [
            float(i.get("close", 0))
            for i in history
        ]

        highs = [
            float(i.get("high", 0))
            for i in history
        ]

        lows = [
            float(i.get("low", 0))
            for i in history
        ]

        hv = self.historical_volatility(closes)

        atr = self.atr(highs, lows, closes)

        latest_price = closes[-1]

        greeks = option_greeks_service.analyze(contract)

        iv = greeks.get("implied_volatility", 0)

        expected = self.expected_move(
            latest_price,
            iv
        )

        regime = self.volatility_regime(
            hv,
            iv
        )

        score = 50

        if regime == "LOW":
            score += 20

        elif regime == "NORMAL":
            score += 30

        elif regime == "HIGH":
            score += 10

        if iv < 25:
            score += 20

        elif iv > 60:
            score -= 10

        score = max(0, min(score, 100))

        if score >= 90:
            grade = "A+"

        elif score >= 80:
            grade = "A"

        elif score >= 70:
            grade = "B"

        elif score >= 60:
            grade = "C"

        else:
            grade = "D"

        return {

            "contract": contract,

            "available": True,

            "historical_volatility": hv,

            "implied_volatility": iv,

            "atr": atr,

            "expected_move": expected,

            "volatility_regime": regime,

            "volatility_score": score,

            "grade": grade,

            "latest_price": latest_price,

            "confidence": min(score + 5, 95)
        }


volatility_engine = VolatilityEngine()