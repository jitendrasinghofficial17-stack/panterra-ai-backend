from fastapi import APIRouter, HTTPException

from app.services.market_regime import market_regime_service

router = APIRouter()


@router.get("/")
def home():
    return {
        "service": "Market Regime Engine",
        "status": "running",
        "version": "1.0",
        "endpoints": [
            "/{contract}",
            "/{contract}/summary",
            "/{contract}/recommendation",
            "/{contract}/health"
        ]
    }


@router.get("/{contract}")
def analyze_market(contract: str):

    try:

        result = market_regime_service.analyze(contract)

        if not result.get("available", False):

            raise HTTPException(
                status_code=404,
                detail=result.get("reason", "Market regime unavailable")
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{contract}/summary")
def summary(contract: str):

    try:

        result = market_regime_service.analyze(contract)

        if not result.get("available", False):

            raise HTTPException(
                status_code=404,
                detail=result.get("reason", "Market regime unavailable")
            )

        return {
            "contract": result["contract"],
            "market_regime": result["market_regime"],
            "market_score": result["market_score"],
            "signal": result["signal"],
            "confidence": result["confidence"]
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{contract}/recommendation")
def recommendation(contract: str):

    try:

        result = market_regime_service.analyze(contract)

        if not result.get("available", False):

            raise HTTPException(
                status_code=404,
                detail=result.get("reason", "Market regime unavailable")
            )

        return {
            "contract": result["contract"],
            "market_regime": result["market_regime"],
            "recommendation": result["recommendation"],
            "confidence": result["confidence"],
            "bullish_probability": result["bullish_probability"],
            "bearish_probability": result["bearish_probability"],
            "sideways_probability": result["sideways_probability"]
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

    try:

        result = market_regime_service.analyze(contract)

        return {
            "service": "Market Regime Engine",
            "status": "healthy" if result.get("available") else "unavailable",
            "contract": contract
        }

    except Exception as e:

        return {
            "service": "Market Regime Engine",
            "status": "error",
            "contract": contract,
            "message": str(e)
        }