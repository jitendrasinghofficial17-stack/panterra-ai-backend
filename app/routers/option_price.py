from fastapi import APIRouter, HTTPException

from app.services.option_price_service import option_price_service

router = APIRouter()


@router.get("/")
def home():
    return {
        "service": "Option Price API",
        "status": "running"
    }


@router.get("/{contract}")
def latest_price(contract: str):

    try:

        latest = option_price_service.latest_price(contract)

        if latest is None:
            raise HTTPException(
                status_code=404,
                detail="No price data found"
            )

        return latest

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{contract}/analysis")
def analyze(contract: str):

    try:

        return option_price_service.analyze(contract)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )