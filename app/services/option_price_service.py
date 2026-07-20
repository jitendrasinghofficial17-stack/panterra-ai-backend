from statistics import mean

from app.services.financialdata_client import client


class OptionPriceService:

    def get_prices(self, contract: str):

        data = client.get_option_prices(contract)

        if not isinstance(data, list):
            return []

        return data

    def latest_price(self, contract: str):

        prices = self.get_prices(contract)

        if not prices:
            return None

        return prices[-1]

    def analyze(self, contract: str):

        prices = self.get_prices(contract)

        if not prices:

            return {
                "contract": contract,
                "available": False
            }

        closes = [
            float(i.get("close", 0))
            for i in prices
        ]

        highs = [
            float(i.get("high", 0))
            for i in prices
        ]

        lows = [
            float(i.get("low", 0))
            for i in prices
        ]

        volumes = [
            float(i.get("volume", 0))
            for i in prices
        ]

        latest = prices[-1]

        latest_close = closes[-1]
        previous_close = closes[-2] if len(closes) > 1 else closes[-1]

        change = latest_close - previous_close

        change_percent = (
            (change / previous_close) * 100
            if previous_close
            else 0
        )

        average_volume = mean(volumes) if volumes else 0

        latest_volume = volumes[-1] if volumes else 0

        if latest_volume > average_volume:
            volume_signal = "HIGH"

        elif latest_volume < average_volume:
            volume_signal = "LOW"

        else:
            volume_signal = "NORMAL"

        highest = max(highs)
        lowest = min(lows)

        if latest_close >= highest:
            trend = "BREAKOUT"

        elif latest_close <= lowest:
            trend = "BREAKDOWN"

        elif latest_close > mean(closes):
            trend = "BULLISH"

        else:
            trend = "BEARISH"

        score = 50

        if trend == "BREAKOUT":
            score += 25

        elif trend == "BULLISH":
            score += 15

        if volume_signal == "HIGH":
            score += 15

        if change_percent > 2:
            score += 10

        score = min(score, 100)

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

            "latest_price": latest_close,

            "daily_change": round(change, 2),

            "daily_change_percent": round(change_percent, 2),

            "highest_price": highest,

            "lowest_price": lowest,

            "average_price": round(mean(closes), 2),

            "average_volume": round(average_volume),

            "latest_volume": round(latest_volume),

            "volume_signal": volume_signal,

            "trend": trend,

            "price_score": score,

            "grade": grade
        }


option_price_service = OptionPriceService()