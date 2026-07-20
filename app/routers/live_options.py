from fastapi import APIRouter, HTTPException

from app.services.option_chain_service import option_chain_service

router = APIRouter()


@router.get("/")
def home():
    return {
        "service": "Live Options API",
        "status": "running"
    }


@router.get("/{symbol}")
def option_chain(symbol: str):
    try:
        return option_chain_service.get_chain(symbol)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/summary")
def summary(symbol: str):
    try:
        return option_chain_service.summary(symbol)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/calls")
def calls(symbol: str):

    try:

        chain = option_chain_service.get_chain(symbol)

        return {
            "symbol": symbol,
            "count": len(chain["calls"]),
            "calls": chain["calls"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/puts")
def puts(symbol: str):

    try:

        chain = option_chain_service.get_chain(symbol)

        return {
            "symbol": symbol,
            "count": len(chain["puts"]),
            "puts": chain["puts"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/expiries")
def expiries(symbol: str):

    try:

        chain = option_chain_service.get_chain(symbol)

        return {
            "symbol": symbol,
            "expiries": chain["expiries"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/expiry/{expiry}")
def contracts_by_expiry(
    symbol: str,
    expiry: str
):

    try:

        chain = option_chain_service.get_chain(symbol)

        contracts = (
            chain["calls"] +
            chain["puts"]
        )

        filtered = option_chain_service.filter_expiry(
            contracts,
            expiry
        )

        return {
            "symbol": symbol,
            "expiry": expiry,
            "contracts": filtered,
            "count": len(filtered)
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{symbol}/atm")
def atm(symbol: str):

    try:

        chain = option_chain_service.get_chain(symbol)

        return {
            "symbol": symbol,
            "atm_strike": chain["atm"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )