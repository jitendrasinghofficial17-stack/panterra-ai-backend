from fastapi import APIRouter

from app.services.dashboard import get_dashboard

router = APIRouter()


@router.get("/")
def home():

    return {
        "status": "success",
        "message": "PANTERRA AI Dashboard API",
        "endpoint": "/dashboard/{symbol}"
    }


@router.get("/{symbol}")
def dashboard(symbol: str):

    return get_dashboard(symbol.upper())