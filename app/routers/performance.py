from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth import get_current_user
from app.models import User

from app.services.performance import (
    get_performance_summary,
    monthly_performance,
    strategy_performance,
    equity_curve
)

router = APIRouter()


@router.get("/")
def home():

    return {
        "status": "success",
        "message": "Performance Analytics API",
        "endpoints": [
            "/performance/summary",
            "/performance/monthly",
            "/performance/strategies",
            "/performance/equity"
        ]
    }


@router.get("/summary")
def performance_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return get_performance_summary(
        db,
        current_user.user_id
    )


@router.get("/monthly")
def monthly_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return monthly_performance(
        db,
        current_user.user_id
    )


@router.get("/strategies")
def strategy_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return strategy_performance(
        db,
        current_user.user_id
    )


@router.get("/equity")
def equity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    return equity_curve(
        db,
        current_user.user_id
    )