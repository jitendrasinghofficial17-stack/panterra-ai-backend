from fastapi import APIRouter, HTTPException

from app.services.ai_option_selector import ai_option_selector

router = APIRouter()


@router.get("/")
def home():
    return {
        "service": "AI Options",
        "status": "running",
        "endpoints": [
            "/{symbol}",
            "/{symbol}/best-call",
            "/{symbol}/best-put",
            "/{symbol}/top-calls",
            "/{symbol}/top-puts",
            "/{symbol}/ranking"
        ]
    }


@router.get("/{symbol}")
def analyze_options(symbol: str):

    try:

        return ai_option_selector.analyze(symbol.upper())

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/best-call")
def best_call(symbol: str):

    try:

        result = ai_option_selector.best_call(symbol.upper())

        if result is None:

            raise HTTPException(
                status_code=404,
                detail="No suitable Call option found"
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/best-put")
def best_put(symbol: str):

    try:

        result = ai_option_selector.best_put(symbol.upper())

        if result is None:

            raise HTTPException(
                status_code=404,
                detail="No suitable Put option found"
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/top-calls")
def top_calls(symbol: str, limit: int = 5):

    try:

        if limit < 1:
            limit = 1

        if limit > 20:
            limit = 20

        return {
            "symbol": symbol.upper(),
            "count": limit,
            "results": ai_option_selector.top_calls(
                symbol.upper(),
                limit
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/top-puts")
def top_puts(symbol: str, limit: int = 5):

    try:

        if limit < 1:
            limit = 1

        if limit > 20:
            limit = 20

        return {
            "symbol": symbol.upper(),
            "count": limit,
            "results": ai_option_selector.top_puts(
                symbol.upper(),
                limit
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/ranking")
def ranking(symbol: str):

    try:

        return {
            "symbol": symbol.upper(),
            "ranking": ai_option_selector.overall_ranking(
                symbol.upper()
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )