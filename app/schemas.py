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
    
# ========================================
# Trade Journal Schemas
# ==========================================

class TradeJournalCreate(BaseModel):
    symbol: str
    trade_type: str
    quantity: int
    entry_price: float
    stop_loss: float | None = None
    target: float | None = None
    strategy: str | None = None
    notes: str | None = None


class TradeJournalUpdate(BaseModel):
    exit_price: float | None = None
    pnl: float | None = None
    notes: str | None = None
    status: str | None = None


class TradeJournalResponse(BaseModel):
    id: int
    user_id: str
    symbol: str
    trade_type: str
    quantity: int
    entry_price: float
    exit_price: float | None = None
    stop_loss: float | None = None
    target: float | None = None
    strategy: str | None = None
    notes: str | None = None
    status: str
    pnl: float

    model_config = ConfigDict(from_attributes=True)