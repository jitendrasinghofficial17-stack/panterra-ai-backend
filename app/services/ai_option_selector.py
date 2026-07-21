from app.services.option_chain_service import option_chain_service
from app.services.option_scoring import option_scoring_service


class AIOptionSelector:

    def _score_contracts(self, contracts):

        scored = []

        for contract in contracts:

            try:

                symbol = (
                    contract.get("symbol")
                    or contract.get("contract")
                    or contract.get("ticker")
                )

                if not symbol:
                    continue

                analysis = option_scoring_service.calculate_score(symbol)

                if analysis.get("available", False):

                    analysis["contract_info"] = contract

                    scored.append(analysis)

            except Exception:
                continue

        scored.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return scored

    def analyze(self, symbol: str):

        chain = option_chain_service.get_chain(symbol)

        calls = option_chain_service.filter_calls(chain)
        puts = option_chain_service.filter_puts(chain)

        scored_calls = self._score_contracts(calls)
        scored_puts = self._score_contracts(puts)

        best_call = scored_calls[0] if scored_calls else None
        best_put = scored_puts[0] if scored_puts else None

        overall = scored_calls + scored_puts

        overall.sort(
            key=lambda x: x["final_score"],
            reverse=True
        )

        return {

            "symbol": symbol,

            "total_calls": len(scored_calls),

            "total_puts": len(scored_puts),

            "best_call": best_call,

            "best_put": best_put,

            "top5_calls": scored_calls[:5],

            "top5_puts": scored_puts[:5],

            "overall_top10": overall[:10]
        }

    def best_call(self, symbol: str):

        result = self.analyze(symbol)

        return result["best_call"]

    def best_put(self, symbol: str):

        result = self.analyze(symbol)

        return result["best_put"]

    def top_calls(self, symbol: str, limit=5):

        result = self.analyze(symbol)

        return result["top5_calls"][:limit]

    def top_puts(self, symbol: str, limit=5):

        result = self.analyze(symbol)

        return result["top5_puts"][:limit]

    def overall_ranking(self, symbol: str):

        result = self.analyze(symbol)

        return result["overall_top10"]


ai_option_selector = AIOptionSelector()