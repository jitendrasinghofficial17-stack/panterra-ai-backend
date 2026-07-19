from fastapi import FastAPI

from .database import Base, engine

app = FastAPI(
    title="PANTERRA AI Trading Platform",
    version="1.0.0"
)

Base.metadata.create_all(bind=engine)

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

# Add authentication, portfolio, watchlist,
# market data and AI routes here as the project grows.
