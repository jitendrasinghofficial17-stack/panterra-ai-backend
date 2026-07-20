from collections import defaultdict


class LiveOptionChainAnalyzer:

    def __init__(self, option_chain):
        self.option_chain = option_chain
        self.calls = option_chain.get("calls", [])
        self.puts = option_chain.get("puts", [])

    def total_call_oi(self):
        return sum(i.get("oi", 0) for i in self.calls)

    def total_put_oi(self):
        return sum(i.get("oi", 0) for i in self.puts)

    def pcr(self):
        call = self.total_call_oi()
        put = self.total_put_oi()

        if call == 0:
            return 0

        return round(put / call, 2)

    def highest_call_oi(self):
        return max(self.calls, key=lambda x: x.get("oi", 0))

    def highest_put_oi(self):
        return max(self.puts, key=lambda x: x.get("oi", 0))

    def support(self):
        return self.highest_put_oi()["strike"]

    def resistance(self):
        return self.highest_call_oi()["strike"]

    def average_iv(self):

        ivs = []

        for i in self.calls:
            ivs.append(i.get("iv", 0))

        for i in self.puts:
            ivs.append(i.get("iv", 0))

        if len(ivs) == 0:
            return 0

        return round(sum(ivs) / len(ivs), 2)

    def max_pain(self):

        pain = defaultdict(float)

        strikes = set()

        for c in self.calls:
            strikes.add(c["strike"])

        for p in self.puts:
            strikes.add(p["strike"])

        strikes = sorted(strikes)

        for strike in strikes:

            loss = 0

            for c in self.calls:
                if strike > c["strike"]:
                    loss += (strike - c["strike"]) * c["oi"]

            for p in self.puts:
                if strike < p["strike"]:
                    loss += (p["strike"] - strike) * p["oi"]

            pain[strike] = loss

        return min(pain, key=pain.get)

    def oi_buildup(self):

        bullish = 0
        bearish = 0

        for p in self.puts:
            if p.get("change_oi", 0) > 0:
                bullish += 1

        for c in self.calls:
            if c.get("change_oi", 0) > 0:
                bearish += 1

        if bullish > bearish:
            return "Bullish"

        if bearish > bullish:
            return "Bearish"

        return "Neutral"

    def recommendation(self):

        pcr = self.pcr()

        buildup = self.oi_buildup()

        if pcr > 1.2 and buildup == "Bullish":
            signal = "BUY CALL"
            confidence = 90

        elif pcr < 0.8 and buildup == "Bearish":
            signal = "BUY PUT"
            confidence = 90

        elif 0.9 <= pcr <= 1.1:
            signal = "IRON CONDOR"
            confidence = 75

        else:
            signal = "WAIT"
            confidence = 60

        return {
            "signal": signal,
            "confidence": confidence
        }

    def analyze(self):

        rec = self.recommendation()

        return {

            "put_call_ratio": self.pcr(),

            "support": self.support(),

            "resistance": self.resistance(),

            "max_pain": self.max_pain(),

            "average_iv": self.average_iv(),

            "oi_buildup": self.oi_buildup(),

            "call_oi": self.total_call_oi(),

            "put_oi": self.total_put_oi(),

            "recommendation": rec["signal"],

            "confidence": rec["confidence"],

            "highest_call_oi": self.highest_call_oi(),

            "highest_put_oi": self.highest_put_oi()
        }


def analyze_live_option_chain(option_chain):

    analyzer = LiveOptionChainAnalyzer(option_chain)

    return analyzer.analyze()