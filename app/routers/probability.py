from fastapi import APIRouter, HTTPException

from app.services.probability_engine import probability_engine

router = APIRouter()


@router.get("/")
def home():
    return {
        "service": "Probability Engine",
        "status": "running",
        "version": "1.0",
        "endpoints": [
            "/{contract}",
            "/{contract}/summary",
            "/{contract}/signal"
        ]
    }


@router.get("/{contract}")
def probability(contract: str):

    try:

        result = probability_engine.predict(contract)

        if not result.get("available", False):

            raise HTTPException(
                status_code=404,
                detail=result.get("reason", "Probability unavailable")
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

        result = probability_engine.predict(contract)

        if not result.get("available", False):

            raise HTTPException(
                status_code=404,
                detail=result.get("reason", "Probability unavailable")
            )

        return {
            "contract": result["contract"],
            "signal": result["signal"],
            "confidence": result["confidence"],
            "bullish_probability": result["bullish_probability"],
            "bearish_probability": result["bearish_probability"],
            "sideways_probability": result["sideways_probability"],
            "grade": result["grade"]
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{contract}/signal")
def signal(contract: str):

    try:

        result = probability_engine.predict(contract)

        if not result.get("available", False):

            raise HTTPException(
                status_code=404,
                detail=result.get("reason", "Probability unavailable")
            )

        return {
            "contract": result["contract"],
            "signal": result["signal"],
            "confidence": result["confidence"],
            "breakout_probability": result["breakout_probability"],
            "reversal_probability": result["reversal_probability"]
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

        result = probability_engine.predict(contract)

        return {
            "service": "Probability Engine",
            "status": "healthy" if result.get("available") else "unavailable",
            "contract": contract
        }

    except Exception as e:

        return {
            "service": "Probability Engine",
            "status": "error",
            "contract": contract,
            "message": str(e)
        }