import requests
import os
from functools import lru_cache

BASE_URL = "https://financialdata.net/api/v1"
API_KEY = os.getenv("FINANCIALDATA_API_KEY")


@lru_cache(maxsize=1)
def get_stock_symbols(offset: int = 0):

    url = f"{BASE_URL}/stock-symbols"

    params = {
        "key": API_KEY,
        "offset": offset
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()


def search_symbol(query: str):

    data = get_stock_symbols()

    results = []

    query = query.lower()

    for item in data:

        symbol = item.get("trading_symbol", "")
        name = item.get("registrant_name", "")

        if (
            query in symbol.lower()
            or query in name.lower()
        ):
            results.append(item)

    return results


def get_symbol(symbol: str):

    data = get_stock_symbols()

    symbol = symbol.upper()

    for item in data:

        if item.get("trading_symbol") == symbol:
            return item

    return None