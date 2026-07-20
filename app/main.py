from fastapi import FastAPI

from app.database import Base, engine

from app.routers.users import router as users_router
from app.routers.portfolio import router as portfolio_router

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