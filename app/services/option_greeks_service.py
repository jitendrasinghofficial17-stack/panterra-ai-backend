from app.services.financialdata_client import client


class OptionGreeksService:

    def get_greeks(self, contract: str):

        data = client.get_option_greeks(contract)

        if isinstance(data, list):

            if len(data) == 0:
                return None

            return data[-1]

        if isinstance(data, dict):
            return data

        return None

    def analyze(self, contract: str):

        greek = self.get_greeks(contract)

        if greek is None:

            return {
                "contract": contract,
                "available": False
            }

        delta = float(greek.get("delta", 0))
        gamma = float(greek.get("gamma", 0))
        theta = float(greek.get("theta", 0))
        vega = float(greek.get("vega", 0))
        rho = float(greek.get("rho", 0))
        iv = float(
            greek.get(
                "implied_volatility",
                greek.get("iv", 0)
            )
        )

        score = 50

        delta_comment = ""
        gamma_comment = ""
        theta_comment = ""
        vega_comment = ""
        rho_comment = ""

        # Delta
        if abs(delta) >= 0.60:
            score += 15
            delta_comment = "Strong directional exposure"

        elif abs(delta) >= 0.30:
            score += 8
            delta_comment = "Moderate directional exposure"

        else:
            delta_comment = "Low directional exposure"

        # Gamma
        if gamma >= 0.05:
            score += 10
            gamma_comment = "High gamma"

        else:
            gamma_comment = "Stable gamma"

        # Theta
        if theta > -0.05:
            score += 10
            theta_comment = "Low time decay"

        else:
            theta_comment = "High time decay"

        # Vega
        if vega >= 0.20:
            score += 10
            vega_comment = "High volatility sensitivity"

        else:
            vega_comment = "Low volatility sensitivity"

        # IV
        if iv <= 25:
            score += 10

        elif iv >= 60:
            score -= 5

        score = max(0, min(score, 100))

        if score >= 90:
            grade = "A+"
            signal = "STRONG BUY"

        elif score >= 80:
            grade = "A"
            signal = "BUY"

        elif score >= 70:
            grade = "B"
            signal = "ACCUMULATE"

        elif score >= 60:
            grade = "C"
            signal = "HOLD"

        else:
            grade = "D"
            signal = "AVOID"

        return {

            "contract": contract,

            "available": True,

            "delta": delta,

            "gamma": gamma,

            "theta": theta,

            "vega": vega,

            "rho": rho,

            "implied_volatility": iv,

            "delta_analysis": delta_comment,

            "gamma_analysis": gamma_comment,

            "theta_analysis": theta_comment,

            "vega_analysis": vega_comment,

            "rho_analysis": rho_comment,

            "greeks_score": score,

            "grade": grade,

            "signal": signal,

            "confidence": min(score + 5, 95)
        }


option_greeks_service = OptionGreeksService()