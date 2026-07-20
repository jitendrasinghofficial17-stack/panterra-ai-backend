from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime
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

    user_id = Column(
        String(20),
        nullable=False
    )

    symbol = Column(
        String(30),
        nullable=False
    )

    quantity = Column(
        Integer,
        nullable=False
    )

    average_price = Column(
        Float,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )


class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        String(20),
        nullable=False
    )

    symbol = Column(
        String(30),
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
class TradeJournal(Base):
    __tablename__ = "trade_journal"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        String(20),
        nullable=False,
        index=True
    )

    symbol = Column(
        String(30),
        nullable=False
    )

    trade_type = Column(
        String(10),
        nullable=False
    )  # BUY / SELL

    quantity = Column(
        Integer,
        nullable=False
    )

    entry_price = Column(
        Float,
        nullable=False
    )

    exit_price = Column(
        Float,
        nullable=True
    )

    stop_loss = Column(
        Float,
        nullable=True
    )

    target = Column(
        Float,
        nullable=True
    )

    strategy = Column(
        String(100),
        nullable=True
    )

    notes = Column(
        String(500),
        nullable=True
    )

    status = Column(
        String(20),
        default="OPEN"
    )  # OPEN / CLOSED

    pnl = Column(
        Float,
        default=0.0
    )

    entry_time = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    exit_time = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )