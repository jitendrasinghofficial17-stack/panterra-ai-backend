from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.option_scoring import option_scoring_service

router = APIRouter()


class ContractList(BaseModel):
    contracts: List[str]


@router.get("/")
def home():
    return {
        "service": "Option Scoring API",
        "status": "running",
        "endpoints": [
            "/{contract}",
            "/rank"
        ]
    }


@router.get("/{contract}")
def score_contract(contract: str):
    """
    Calculate AI score for a single option contract.
    """

    try:

        result = option_scoring_service.calculate_score(contract)

        if not result.get("available", False):
            raise HTTPException(
                status_code=404,
                detail=result.get("reason", "Data unavailable")
            )

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/rank")
def rank_contracts(request: ContractList):
    """
    Rank multiple option contracts.
    """

    try:

        results = option_scoring_service.rank_contracts(
            request.contracts
        )

        return {
            "total_contracts": len(request.contracts),
            "ranked_contracts": len(results),
            "results": results
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/{contract}/summary")
def contract_summary(contract: str):
    """
    Lightweight summary for dashboard/cards.
    """

    try:

        result = option_scoring_service.calculate_score(contract)

        if not result.get("available", False):
            raise HTTPException(
                status_code=404,
                detail=result.get("reason", "Data unavailable")
            )

        return {
            "contract": result["contract"],
            "final_score": result["final_score"],
            "grade": result["grade"],
            "signal": result["signal"],
            "confidence": result["confidence"],
            "trend": result["trend"],
            "volume_signal": result["volume_signal"]
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )