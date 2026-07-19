from fastapi import APIRouter, HTTPException
from app.schemas import UserRegister, UserResponse
from app.auth import hash_password, verify_password
import uuid

router = APIRouter()


# Temporary in-memory database
# (We'll replace this with PostgreSQL in the next step.)

users_db = {}


@router.get("/")
def users_home():
    return {
        "message": "Users API Working"
    }


@router.post(
    "/register",
    response_model=UserResponse
)
def register_user(user: UserRegister):

    # Check mobile number
    if user.mobile_number in users_db:
        raise HTTPException(
            status_code=400,
            detail="Mobile number already registered"
        )

    # Check email
    if user.email:
        for u in users_db.values():
            if u["email"] == user.email:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )

    user_id = "USR-" + uuid.uuid4().hex[:8].upper()

    users_db[user.mobile_number] = {
        "user_id": user_id,
        "full_name": user.full_name,
        "mobile_number": user.mobile_number,
        "email": user.email,
        "password": hash_password(user.password)
    }

    return {
        "status": "success",
        "message": "Registration Successful",
        "user_id": user_id
    }


@router.post("/login")
def login(
    mobile_number: str,
    password: str
):

    if mobile_number not in users_db:
        raise HTTPException(
            status_code=401,
            detail="Invalid Mobile Number"
        )

    user = users_db[mobile_number]

    if not verify_password(
        password,
        user["password"]
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    return {
        "status": "success",
        "message": "Login Successful",
        "user_id": user["user_id"]
    }