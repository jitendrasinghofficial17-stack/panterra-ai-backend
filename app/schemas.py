from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict


# ----------------------------
# User Registration
# ----------------------------

class UserRegister(BaseModel):
    full_name: str
    mobile_number: str
    email: Optional[EmailStr] = None
    password: str


class UserResponse(BaseModel):
    status: str
    message: str
    user_id: str


# ----------------------------
# User Login
# ----------------------------

class UserLogin(BaseModel):
    mobile_number: str
    password: str


# ----------------------------
# JWT Token
# ----------------------------

class Token(BaseModel):
    status: str
    message: str
    access_token: str
    token_type: str
    user_id: str
    full_name: str
    mobile_number: str


# ----------------------------
# User Profile
# ----------------------------

class UserProfile(BaseModel):
    user_id: str
    full_name: str
    mobile_number: str
    email: Optional[EmailStr] = None
    mobile_verified: bool
    email_verified: bool
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ----------------------------
# Update Profile
# ----------------------------

class UpdateProfile(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


# ----------------------------
# Change Password
# ----------------------------

class ChangePassword(BaseModel):
    old_password: str
    new_password: str