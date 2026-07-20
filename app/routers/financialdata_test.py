from fastapi import APIRouter, HTTPException

from app.services.financialdata_client import client

router = APIRouter()


@router.get("/")
def home():
    return {
        "service": "FinancialData Test API",
        "status": "running"
    }


@router.get("/stock-symbols")
def stock_symbols():
    try:
        return client.get_stock_symbols()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/index-quotes")
def index_quotes():
    try:
        return client.get_index_quotes(
            [
                "^GSPC",
                "^DJI",
                "^IXIC"
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/index-prices/{identifier}")
def index_prices(identifier: str):
    try:
        return client.get_index_prices(identifier)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/option-chain/{symbol}")
def option_chain(symbol: str):
    try:
        return client.get_option_chain(symbol)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/option-prices/{contract}")
def option_prices(contract: str):
    try:
        return client.get_option_prices(contract)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/option-greeks/{contract}")
def option_greeks(contract: str):
    try:
        return client.get_option_greeks(contract)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/futures-symbols")
def futures_symbols():
    try:
        return client.get_futures_symbols()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/futures-prices/{symbol}")
def futures_prices(symbol: str):
    try:
        return client.get_futures_prices(symbol)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/crypto-symbols")
def crypto_symbols():
    try:
        return client.get_crypto_symbols()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/forex-symbols")
def forex_symbols():
    try:
        return client.get_forex_symbols()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )