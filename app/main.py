from dotenv import load_dotenv
load_dotenv()

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
from app.routers.backtest import router as backtest_router
from app.routers.prediction import router as prediction_router
from app.routers.recommendation import router as recommendation_router
from app.routers.symbols import router as symbols_router
from app.routers.portfolio_analyzer import  router as portfolio_analyzer_router
from app.routers.dashboard import router as dashboard_router
from app.routers.trade_journal import router as trade_journal_router
from app.routers.performance import router as performance_router
from app.routers.paper_trading import router as paper_trading_router
from app.routers.ai_trade_review import router as ai_trade_review_router
from app.routers.strategy_builder import router as strategy_builder_router
from app.routers.options_strategy import router as options_strategy_router
from app.routers.options_chain_ai import router as options_chain_ai_router
from app.routers.live_options_chain import router as live_options_chain_router
from app.routers.financialdata_test import router as financialdata_test_router
from app.routers.live_options import router as live_options_router

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
app.include_router(
    backtest_router,
    prefix="/backtest",
    tags=["Backtest"]
)
app.include_router(
    prediction_router,
    prefix="/prediction",
    tags=["AI Prediction"]
)
app.include_router(
    recommendation_router,
    prefix="/recommendation",
    tags=["AI Recommendation"]
)
app.include_router(
    symbols_router,
    prefix="/symbols",
    tags=["Symbols"]
)
app.include_router(
    portfolio_analyzer_router,
    prefix="/portfolio-analyzer",
    tags=["Portfolio Analyzer"]
)
app.include_router(
    dashboard_router,
    prefix="/dashboard",
    tags=["AI Dashboard"]
)
app.include_router(
    trade_journal_router,
    prefix="/trade-journal",
    tags=["Trade Journal"]
)
app.include_router(
    performance_router,
    prefix="/performance",
    tags=["Performance Analytics"]
)
app.include_router(
    paper_trading_router,
    prefix="/paper-trading",
    tags=["Paper Trading"]
)
app.include_router(
    ai_trade_review_router,
    prefix="/ai-trade-review",
    tags=["AI Trade Review"]
)
app.include_router(
    strategy_builder_router,
    prefix="/strategy-builder",
    tags=["AI Strategy Builder"]
)
app.include_router(
    options_strategy_router,
    prefix="/options-strategy",
    tags=["AI Options Strategy"]
)
app.include_router(
    options_chain_ai_router,
    prefix="/options-chain-ai",
    tags=["AI Options Chain"]
)
app.include_router(
    live_options_chain_router,
    prefix="/live-options-chain",
    tags=["Live Options Chain AI"]
)
app.include_router(
    financialdata_test_router,
    prefix="/financialdata-test",
    tags=["FinancialData Test"]
)
app.include_router(
    live_options_router,
    prefix="/live-options",
    tags=["Live Options"]
)