from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models import User
from app.schemas import UserRegister, UserResponse
from app.auth import hash_password

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserRegister,
    db: Session = Depends(get_db)
):

    # Check mobile number
    existing_mobile = db.query(User).filter(
        User.mobile_number == user.mobile_number
    ).first()

    if existing_mobile:
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered."
        )

    # Check email
    if user.email:
        existing_email = db.query(User).filter(
            User.email == user.email
        ).first()

        if existing_email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered."
            )

    new_user = User(
        user_id="USR" + uuid.uuid4().hex[:8].upper(),
        full_name=user.full_name,
        mobile_number=user.mobile_number,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserResponse(
        status="success",
        message="Registration Successful",
        user_id=new_user.user_id
    )


@router.get("/")
def users_home():
    return {
        "message": "Users API Working"
    }


@router.get("/login")
def login_info():
    return {
        "message": "User Login Endpoint"
    }