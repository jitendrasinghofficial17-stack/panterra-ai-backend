from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )

    full_name = Column(
        String(100),
        nullable=False
    )

    mobile_number = Column(
        String(15),
        unique=True,
        nullable=False,
        index=True
    )

    email = Column(
        String(120),
        unique=True,
        nullable=True,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    mobile_verified = Column(
        Boolean,
        default=False
    )

    email_verified = Column(
        Boolean,
        default=False
    )

    status = Column(
        String(20),
        default="ACTIVE"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    last_login = Column(
        DateTime(timezone=True),
        nullable=True
    )


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String(20), nullable=False)

    symbol = Column(String(30), nullable=False)

    quantity = Column(Integer, nullable=False)

    average_price = Column(nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(String(20), nullable=False)

    symbol = Column(String(30), nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )