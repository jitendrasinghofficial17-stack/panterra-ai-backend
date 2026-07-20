from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Watchlist, User
from app.auth import get_current_user

router = APIRouter()


@router.get("/")
def watchlist_home():
    return {
        "status": "success",
        "message": "Watchlist API Working"
    }


@router.post("/add")
def add_stock(
    symbol: str,
    company_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    existing = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.user_id,
        Watchlist.symbol == symbol
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Stock already exists in watchlist"
        )

    stock = Watchlist(
        user_id=current_user.user_id,
        symbol=symbol.upper(),
        company_name=company_name
    )

    db.add(stock)
    db.commit()
    db.refresh(stock)

    return {
        "status": "success",
        "message": "Stock added successfully",
        "watchlist": {
            "id": stock.id,
            "symbol": stock.symbol,
            "company_name": stock.company_name
        }
    }


@router.get("/my")
def my_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stocks = db.query(Watchlist).filter(
        Watchlist.user_id == current_user.user_id
    ).all()

    return {
        "status": "success",
        "count": len(stocks),
        "watchlist": stocks
    }


@router.delete("/{watchlist_id}")
def delete_stock(
    watchlist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    stock = db.query(Watchlist).filter(
        Watchlist.id == watchlist_id,
        Watchlist.user_id == current_user.user_id
    ).first()

    if stock is None:
        raise HTTPException(
            status_code=404,
            detail="Stock not found"
        )

    db.delete(stock)
    db.commit()

    return {
        "status": "success",
        "message": "Stock removed successfully"
    }