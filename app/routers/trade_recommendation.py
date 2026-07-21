from fastapi import APIRouter, HTTPException

from app.services.trade_recommendation import trade_recommendation_service

router = APIRouter()


@router.get("/")
def home():
    return {
        "service": "AI Trade Recommendation Engine",
        "status": "running",
        "version": "1.0",
        "endpoints": [
            "/{symbol}/{contract}",
            "/{symbol}/{contract}/summary",
            "/{symbol}/{contract}/signal",
            "/{symbol}/{contract}/health"
        ]
    }


@router.get("/{symbol}/{contract}")
def analyze(symbol: str, contract: str):

    try:

        result = trade_recommendation_service.analyze(
            symbol,
            contract
        )

        if not result.get("available", False):
            raise HTTPException(
                status_code=404,
                detail=result.get(
                    "reason",
                    "Trade recommendation unavailable"
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


@router.get("/{symbol}/{contract}/summary")
def summary(symbol: str, contract: str):

    try:

        result = trade_recommendation_service.analyze(
            symbol,
            contract
        )

        if not result.get("available", False):
            raise HTTPException(
                status_code=404,
                detail=result.get(
                    "reason",
                    "Trade recommendation unavailable"
                )
            )

        return {
            "symbol": result["symbol"],
            "contract": result["contract"],
            "trade_action": result["trade_action"],
            "overall_score": result["overall_score"],
            "confidence": result["confidence"],
            "risk_level": result["risk_level"]
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/{contract}/signal")
def signal(symbol: str, contract: str):

    try:

        result = trade_recommendation_service.analyze(
            symbol,
            contract
        )

        if not result.get("available", False):
            raise HTTPException(
                status_code=404,
                detail=result.get(
                    "reason",
                    "Trade recommendation unavailable"
                )
            )

        return {
            "symbol": result["symbol"],
            "contract": result["contract"],
            "trade_action": result["trade_action"],
            "market_regime": result["market_regime"],
            "institutional_sentiment": result["institutional_sentiment"],
            "probability_signal": result["probability_signal"],
            "recommendation": result["recommendation"]
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/{contract}/health")
def health(symbol: str, contract: str):

    try:

        result = trade_recommendation_service.analyze(
            symbol,
            contract
        )

        return {
            "service": "AI Trade Recommendation Engine",
            "status": (
                "healthy"
                if result.get("available")
                else "unavailable"
            ),
            "symbol": symbol,
            "contract": contract
        }

    except Exception as e:

        return {
            "service": "AI Trade Recommendation Engine",
            "status": "error",
            "symbol": symbol,
            "contract": contract,
            "message": str(e)
        }