from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PortfolioCreate(BaseModel):
    symbol: str
    quantity: int
    average_price: float


class WatchlistCreate(BaseModel):
    symbol: str


class Message(BaseModel):
    message: str
