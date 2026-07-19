from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    full_name: str
    mobile_number: str
    email: Optional[EmailStr] = None
    password: str


class UserResponse(BaseModel):
    status: str
    message: str
    user_id: str