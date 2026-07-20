from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserResponse
from app.auth import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()


@router.get("/")
def users_home():
    return {
        "status": "success",
        "message": "Users API Working"
    }


@router.post(
    "/register",
    response_model=UserResponse
)
def register_user(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    existing_mobile = db.query(User).filter(
        User.mobile_number == user.mobile_number
    ).first()

    if existing_mobile:
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )

    if user.email:

        existing_email = db.query(User).filter(
            User.email == user.email
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )

    user_id = "USR-" + uuid.uuid4().hex[:8].upper()

    new_user = User(
        user_id=user_id,
        full_name=user.full_name,
        mobile_number=user.mobile_number,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "message": "Registration Successful",
        "user_id": new_user.user_id
    }


@router.post("/login")
def login(
    mobile_number: str,
    password: str,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.mobile_number == mobile_number
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Mobile Number"
        )

    if not verify_password(
        password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    access_token = create_access_token(
        {
            "user_id": user.user_id,
            "mobile_number": user.mobile_number
        }
    )

    return {
        "status": "success",
        "message": "Login Successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.user_id,
        "full_name": user.full_name,
        "mobile_number": user.mobile_number
    }