from fastapi import FastAPI

from app.database import Base, engine

from app.routers.users import router as users_router
from app.routers.portfolio import router as portfolio_router
from app.routers.watchlist import router as watchlist_router
from app.routers.market import router as market_router
from app.routers.signals import router as signals_router
from app.routers.history import router as history_router
from app.routers.risk_manager import router as risk_manager_router
from app.routers.trade_manager import router as trade_manager_router
from app.routers.scanner import router as scanner_router
app = FastAPI(
    title="PANTERRA AI Backend",
    version="1.0.0",
    description="AI Powered Trading Platform Backend"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Root API
@app.get("/")
def root():
    return {
        "status": "success",
        "message": "Welcome to PANTERRA AI Backend",
        "version": "1.0.0"
    }

# Users API
app.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)

# Portfolio API
app.include_router(
    portfolio_router,
    prefix="/portfolio",
    tags=["Portfolio"]
)
# Watchlist API
app.include_router(
    watchlist_router,
    prefix="/watchlist",
    tags=["Watchlist"]
)
# Market API
app.include_router(
    market_router,
    prefix="/market",
    tags=["Market Data"]
)
# AI Signals API
app.include_router(
    signals_router,
    prefix="/signals",
    tags=["AI Signals"]
)
app.include_router(
    history_router,
    prefix="/history",
    tags=["History"]
)
app.include_router(
    risk_manager_router,
    prefix="/risk-manager",
    tags=["Risk Manager"]
)
app.include_router(
    trade_manager_router,
    prefix="/trade-manager",
    tags=["Trade Manager"]
)
app.include_router(
    scanner_router,
    prefix="/scanner",
    tags=["Scanner"]
)