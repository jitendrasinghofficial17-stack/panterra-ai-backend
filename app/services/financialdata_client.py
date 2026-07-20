import os
import requests
from typing import Dict, List, Optional

BASE_URL = "https://financialdata.net/api/v1"


class FinancialDataClient:

    def __init__(self):

        self.api_key = os.getenv("FINANCIALDATA_API_KEY")

        if not self.api_key:
            raise ValueError(
                "FINANCIALDATA_API_KEY environment variable not found."
            )

    def _request(self, endpoint: str, params: Optional[Dict] = None):

        if params is None:
            params = {}

        params["key"] = self.api_key

        url = f"{BASE_URL}/{endpoint}"

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        response.raise_for_status()

        return response.json()

    # ----------------------------
    # Option Chain
    # ----------------------------

    def get_option_chain(self, identifier: str):

        return self._request(
            "option-chain",
            {
                "identifier": identifier
            }
        )

    # ----------------------------
    # Option Prices
    # ----------------------------

    def get_option_prices(self, contract: str):

        return self._request(
            "option-prices",
            {
                "identifier": contract
            }
        )

    # ----------------------------
    # Option Greeks
    # ----------------------------

    def get_option_greeks(self, contract: str):

        return self._request(
            "option-greeks",
            {
                "identifier": contract
            }
        )

    # ----------------------------
    # Futures Symbols
    # ----------------------------

    def get_futures_symbols(self):

        return self._request(
            "futures-symbols"
        )

    # ----------------------------
    # Futures Prices
    # ----------------------------

    def get_futures_prices(self, identifier: str):

        return self._request(
            "futures-prices",
            {
                "identifier": identifier
            }
        )

    # ----------------------------
    # Index Quotes
    # ----------------------------

    def get_index_quotes(
        self,
        identifiers: List[str]
    ):

        return self._request(
            "index-quotes",
            {
                "identifiers": ",".join(identifiers)
            }
        )

    # ----------------------------
    # Index Prices
    # ----------------------------

    def get_index_prices(self, identifier: str):

        return self._request(
            "index-prices",
            {
                "identifier": identifier
            }
        )

    # ----------------------------
    # Stock Symbols
    # ----------------------------

    def get_stock_symbols(self):

        return self._request(
            "stock-symbols"
        )

    # ----------------------------
    # Crypto Symbols
    # ----------------------------

    def get_crypto_symbols(self):

        return self._request(
            "crypto-symbols"
        )

    # ----------------------------
    # Forex Symbols
    # ----------------------------

    def get_forex_symbols(self):

        return self._request(
            "forex-symbols"
        )


client = FinancialDataClient()