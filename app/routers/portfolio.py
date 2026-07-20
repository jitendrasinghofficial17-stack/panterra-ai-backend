from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Portfolio, User
from app.auth import get_current_user

router = APIRouter()


@router.post("/create")
def create_portfolio(
    portfolio_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = Portfolio(
        user_id=current_user.user_id,
        portfolio_name=portfolio_name
    )

    db.add(portfolio)
    db.commit()
    db.refresh(portfolio)

    return {
        "status": "success",
        "message": "Portfolio created successfully",
        "portfolio": {
            "id": portfolio.id,
            "portfolio_name": portfolio.portfolio_name,
            "user_id": portfolio.user_id
        }
    }


@router.get("/")
def get_portfolios(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolios = db.query(Portfolio).filter(
        Portfolio.user_id == current_user.user_id
    ).all()

    return {
        "status": "success",
        "count": len(portfolios),
        "portfolios": portfolios
    }


@router.delete("/{portfolio_id}")
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    portfolio = db.query(Portfolio).filter(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.user_id
    ).first()

    if portfolio is None:
        raise HTTPException(
            status_code=404,
            detail="Portfolio not found"
        )

    db.delete(portfolio)
    db.commit()

    return {
        "status": "success",
        "message": "Portfolio deleted successfully"
    }