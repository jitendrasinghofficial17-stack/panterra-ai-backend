from fastapi import APIRouter, HTTPException, Body

from app.services.live_options_chain import analyze_live_option_chain

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Live Options Chain AI API",
        "version": "1.0",
        "status": "running"
    }


@router.post("/analyze")
def analyze(
    option_chain: dict = Body(
        ...,
        example={
            "calls": [
                {
                    "strike": 24000,
                    "oi": 120000,
                    "change_oi": 5400,
                    "iv": 14.2
                },
                {
                    "strike": 24100,
                    "oi": 150000,
                    "change_oi": 7200,
                    "iv": 14.8
                }
            ],
            "puts": [
                {
                    "strike": 23900,
                    "oi": 180000,
                    "change_oi": 9200,
                    "iv": 15.1
                },
                {
                    "strike": 23800,
                    "oi": 140000,
                    "change_oi": 6400,
                    "iv": 15.7
                }
            ]
        }
    )
):

    if not isinstance(option_chain, dict):
        raise HTTPException(
            status_code=400,
            detail="Invalid request body"
        )

    if "calls" not in option_chain:
        raise HTTPException(
            status_code=400,
            detail="Calls data missing"
        )

    if "puts" not in option_chain:
        raise HTTPException(
            status_code=400,
            detail="Puts data missing"
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

    try:

        result = analyze_live_option_chain(option_chain)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/health")
def health():

    return {
        "service": "Live Options Chain AI",
        "status": "healthy"
    }