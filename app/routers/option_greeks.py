from fastapi import APIRouter, HTTPException

from app.services.option_greeks_service import option_greeks_service

router = APIRouter()


@router.get("/")
def home():
    return {
        "service": "Option Greeks API",
        "status": "running",
        "endpoints": [
            "/{contract}",
            "/{contract}/analysis"
        ]
    }


@router.get("/{contract}")
def get_option_greeks(contract: str):
    """
    Returns the raw option greeks.
    """

    try:

        data = option_greeks_service.get_greeks(contract)

        if data is None:
            raise HTTPException(
                status_code=404,
                detail="Greeks data not found"
            )

        return data

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{contract}/analysis")
def analyze_option_greeks(contract: str):
    """
    Returns AI analysis of option greeks.
    """

    try:

        result = option_greeks_service.analyze(contract)

        if not result.get("available", False):
            raise HTTPException(
                status_code=404,
                detail="Greeks data not available"
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )