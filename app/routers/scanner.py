from fastapi import APIRouter
from app.services.scanner import scan_market

router = APIRouter()


@router.get("/")
def scanner():

    return {

        "status":"success",

        "stocks":scan_market()

    }