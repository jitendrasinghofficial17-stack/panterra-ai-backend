from fastapi import FastAPI
import os
import httpx

app = FastAPI(
    title="Panterra AI Trading Platform",
    version="1.1.0",
    description="Production AI Trading Backend"
)

API_KEY = os.getenv("FINANCIALDATA_API_KEY")


@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Welcome to Panterra AI Trading Platform",
        "version": "1.1.0"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }


@app.get("/stock/{symbol}")
async def get_stock(symbol: str):
    if not API_KEY:
        return {
            "error": "FINANCIALDATA_API_KEY is not configured."
        }

    url = "https://financialdata.net/api/v1/stock-symbols"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params={"key": API_KEY}
        )

    return response.json()
