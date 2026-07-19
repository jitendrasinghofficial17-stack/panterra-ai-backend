from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def users_home():
    return {
        "message": "Users API Working"
    }


@router.get("/register")
def register_info():
    return {
        "message": "User Registration Endpoint"
    }


@router.get("/login")
def login_info():
    return {
        "message": "User Login Endpoint"
    }
