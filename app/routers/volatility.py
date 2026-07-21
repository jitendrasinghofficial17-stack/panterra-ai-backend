from fastapi import APIRouter, HTTPException

from app.services.volatility_engine import volatility_engine

router = APIRouter()


@router.get("/")
def home():
    return {
        "service": "Volatility Engine",
        "status": "running",
        "version": "1.0",
        "endpoints": [
            "/{contract}",
            "/{contract}/analysis",
            "/{contract}/summary"
        ]
    }


@router.get("/{contract}")
def get_volatility(contract: str):
    """
    Returns complete volatility analysis.
    """

    try:

        result = volatility_engine.analyze(contract)

        if not result.get("available", False):
            raise HTTPException(
                status_code=404,
                detail="Volatility data not available"
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{contract}/analysis")
def analyze_volatility(contract: str):
    """
    Returns AI volatility analysis.
    """

    try:

        result = volatility_engine.analyze(contract)

        if not result.get("available", False):
            raise HTTPException(
                status_code=404,
                detail="Volatility analysis unavailable"
            )

        return {
            "contract": result["contract"],
            "historical_volatility": result["historical_volatility"],
            "implied_volatility": result["implied_volatility"],
            "atr": result["atr"],
            "expected_move": result["expected_move"],
            "volatility_regime": result["volatility_regime"],
            "volatility_score": result["volatility_score"],
            "grade": result["grade"],
            "confidence": result["confidence"]
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{contract}/summary")
def volatility_summary(contract: str):
    """
    Lightweight summary for dashboard.
    """

    try:

        result = volatility_engine.analyze(contract)

        if not result.get("available", False):
            raise HTTPException(
                status_code=404,
                detail="Volatility data unavailable"
            )

        return {
            "contract": result["contract"],
            "latest_price": result["latest_price"],
            "volatility_score": result["volatility_score"],
            "grade": result["grade"],
            "volatility_regime": result["volatility_regime"],
            "expected_move": result["expected_move"]
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{contract}/health")
def health(contract: str):
    """
    Health check for the volatility engine.
    """

    try:

        result = volatility_engine.analyze(contract)

        return {
            "service": "Volatility Engine",
            "status": "healthy" if result.get("available") else "unavailable",
            "contract": contract
        }

    except Exception as e:

        return {
            "service": "Volatility Engine",
            "status": "error",
            "contract": contract,
            "message": str(e)
        }