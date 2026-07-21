from fastapi import APIRouter, HTTPException

from app.services.institutional_flow import institutional_flow_service

router = APIRouter()


@router.get("/")
def home():
    return {
        "service": "Institutional Flow Engine",
        "status": "running",
        "version": "1.0",
        "endpoints": [
            "/{symbol}",
            "/contract/{contract}",
            "/{symbol}/summary",
            "/{symbol}/health"
        ]
    }


@router.get("/{symbol}")
def analyze_symbol(symbol: str):

    try:

        result = institutional_flow_service.analyze(symbol)

        if not result.get("available", False):

            raise HTTPException(
                status_code=404,
                detail=result.get(
                    "reason",
                    "Institutional flow unavailable"
                )
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/contract/{contract}")
def analyze_contract(contract: str):

    try:

        result = institutional_flow_service.analyze_contract(contract)

        if not result.get("available", False):

            raise HTTPException(
                status_code=404,
                detail="Contract analysis unavailable"
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/summary")
def summary(symbol: str):

    try:

        result = institutional_flow_service.analyze(symbol)

        if not result.get("available", False):

            raise HTTPException(
                status_code=404,
                detail=result.get(
                    "reason",
                    "Institutional flow unavailable"
                )
            )

        return {
            "symbol": result["symbol"],
            "market_sentiment": result["market_sentiment"],
            "institutional_score": result["institutional_score"],
            "confidence": result["confidence"],
            "recommendation": result["recommendation"],
            "put_call_ratio": result["put_call_ratio"]
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/health")
def health(symbol: str):

    try:

        result = institutional_flow_service.analyze(symbol)

        return {
            "service": "Institutional Flow Engine",
            "status": (
                "healthy"
                if result.get("available")
                else "unavailable"
            ),
            "symbol": symbol
        }

    except Exception as e:

        return {
            "service": "Institutional Flow Engine",
            "status": "error",
            "symbol": symbol,
            "message": str(e)
        }