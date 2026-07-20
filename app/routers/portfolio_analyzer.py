from fastapi import APIRouter, Query

from app.services.portfolio_analyzer import analyze_portfolio

router = APIRouter()


@router.get("/")
def portfolio_analyzer(

    symbols: str = Query(
        ...,
        description="Comma separated symbols"
    )

):

    symbol_list = [

        s.strip().upper()

        for s in symbols.split(",")

        if s.strip()

    ]

    return analyze_portfolio(symbol_list)