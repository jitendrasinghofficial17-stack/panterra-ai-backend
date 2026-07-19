from fastapi import FastAPI

from .database import Base, engine
from .routers.users import router as users_router

app = FastAPI(
    title="PANTERRA AI Trading Platform",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

app.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)


@app.get("/")
def root():
    return {
        "message": "PANTERRA AI Trading Platform API",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }