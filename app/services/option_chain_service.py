from collections import defaultdict
from typing import Dict, List, Optional

from app.services.financialdata_client import client


class OptionChainService:

    def get_chain(self, symbol: str):

        data = client.get_option_chain(symbol)

        if not isinstance(data, list):
            return {
                "symbol": symbol,
                "contracts": [],
                "calls": [],
                "puts": [],
                "expiries": [],
                "atm": None
            }

        calls = []
        puts = []

        expiries = set()

        strikes = []

        for contract in data:

            expiry = contract.get("expiration_date")
            strike = float(contract.get("strike_price", 0))
            option_type = contract.get("put_or_call", "").upper()

            expiries.add(expiry)
            strikes.append(strike)

            item = {
                "symbol": contract.get("trading_symbol"),
                "contract_name": contract.get("contract_name"),
                "expiry": expiry,
                "strike": strike,
                "type": option_type,
                "registrant_name": contract.get("registrant_name")
            }

            if option_type == "CALL":
                calls.append(item)

            elif option_type == "PUT":
                puts.append(item)

        calls.sort(key=lambda x: (x["expiry"], x["strike"]))
        puts.sort(key=lambda x: (x["expiry"], x["strike"]))

        return {
            "symbol": symbol,
            "contracts": len(data),
            "calls": calls,
            "puts": puts,
            "expiries": sorted(list(expiries)),
            "atm": self.detect_atm(calls, puts)
        }

    def detect_atm(
        self,
        calls: List[Dict],
        puts: List[Dict]
    ):

        if not calls:
            return None

        strikes = sorted(
            list(
                {
                    c["strike"] for c in calls
                }
            )
        )

        if not strikes:
            return None

        return strikes[len(strikes) // 2]

    def group_by_expiry(
        self,
        contracts: List[Dict]
    ):

        grouped = defaultdict(list)

        for contract in contracts:
            grouped[contract["expiry"]].append(contract)

        return grouped

    def filter_expiry(
        self,
        contracts: List[Dict],
        expiry: str
    ):

        return [
            c
            for c in contracts
            if c["expiry"] == expiry
        ]

    def filter_calls(
        self,
        contracts: List[Dict]
    ):

        return [
            c
            for c in contracts
            if c["type"] == "CALL"
        ]

    def filter_puts(
        self,
        contracts: List[Dict]
    ):

        return [
            c
            for c in contracts
            if c["type"] == "PUT"
        ]

    def nearest_expiry(
        self,
        expiries: List[str]
    ):

        if not expiries:
            return None

        return sorted(expiries)[0]

    def summary(self, symbol: str):

        chain = self.get_chain(symbol)

        return {

            "symbol": symbol,

            "contracts": chain["contracts"],

            "call_contracts": len(chain["calls"]),

            "put_contracts": len(chain["puts"]),

            "nearest_expiry": self.nearest_expiry(
                chain["expiries"]
            ),

            "atm_strike": chain["atm"]
        }


option_chain_service = OptionChainService()