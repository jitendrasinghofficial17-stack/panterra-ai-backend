from fastapi import APIRouter, Query

from app.services.symbols import (
    get_stock_symbols,
    search_symbol,
    get_symbol
)

router = APIRouter()


@router.get("/")
def all_symbols():

    return get_stock_symbols()


@router.get("/search")
def search(q: str = Query(...)):

    return search_symbol(q)


@router.get("/{symbol}")
def symbol(symbol: str):

    result = get_symbol(symbol)

    if result:
        return result

    return {
        "message": "Symbol not found"
    }