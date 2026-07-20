from fastapi import APIRouter, HTTPException, Body

from app.services.options_chain_ai import get_options_chain_ai

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "AI Options Chain API",
        "status": "running"
    }


@router.post("/analyze")
def analyze_option_chain(
    option_chain: dict = Body(
        ...,
        example={
            "calls": [
                {
                    "strike": 24000,
                    "oi": 120000,
                    "change_oi": 5200,
                    "iv": 14.6
                },
                {
                    "strike": 24100,
                    "oi": 165000,
                    "change_oi": 7300,
                    "iv": 15.2
                }
            ],
            "puts": [
                {
                    "strike": 23900,
                    "oi": 180000,
                    "change_oi": 9600,
                    "iv": 15.5
                },
                {
                    "strike": 23800,
                    "oi": 145000,
                    "change_oi": 6400,
                    "iv": 15.8
                }
            ]
        }
    )
):

    if "calls" not in option_chain:
        raise HTTPException(
            status_code=400,
            detail="Missing calls data"
        )

    if "puts" not in option_chain:
        raise HTTPException(
            status_code=400,
            detail="Missing puts data"
        )

    if len(option_chain["calls"]) == 0:
        raise HTTPException(
            status_code=400,
            detail="Calls list is empty"
        )

    if len(option_chain["puts"]) == 0:
        raise HTTPException(
            status_code=400,
            detail="Puts list is empty"
        )

    return get_options_chain_ai(option_chain)