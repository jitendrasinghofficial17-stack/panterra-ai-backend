from fastapi import APIRouter, Query

from app.services.scanner import scan_market

router = APIRouter()


@router.get("/")
def scanner(

    symbols: str | None = Query(
        default=None,
        description="Comma separated symbols"
    ),

    min_score: int = Query(
        default=0,
        ge=0,
        le=100
    ),

    action: str | None = Query(
        default=None
    ),

    limit: int = Query(
        default=20,
        ge=1,
        le=100
    )

):

    symbol_list = None

    if symbols:
        symbol_list = [
            s.strip().upper()
            for s in symbols.split(",")
            if s.strip()
        ]

    return scan_market(
        symbols=symbol_list,
        min_score=min_score,
        action=action,
        limit=limit
    )