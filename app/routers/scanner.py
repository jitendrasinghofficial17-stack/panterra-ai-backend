from fastapi import APIRouter
from app.services.scanner import scan_market

router = APIRouter()


@router.get("/")
def scanner():

    return {
        "status": "success",
        "scanner": "Panterra AI Scanner v2",
        "stocks": scan_market()
    }