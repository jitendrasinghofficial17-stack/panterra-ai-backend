from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    full_name: str
    mobile_number: str
    email: Optional[EmailStr] = None
    password: str


class UserLogin(BaseModel):
    mobile_number: str
    password: str


class OTPRequest(BaseModel):
    mobile_number: str


class OTPVerify(BaseModel):
    mobile_number: str
    otp: str


class PortfolioCreate(BaseModel):
    symbol: str
    quantity: int
    average_price: float


class WatchlistCreate(BaseModel):
    symbol: str


class Message(BaseModel):
    message: str