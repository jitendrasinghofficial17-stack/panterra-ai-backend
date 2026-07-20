from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def signals_home():
    return {
        "status": "success",
        "message": "AI Signals API Working"
    }


@router.get("/{symbol}")
def get_signal(symbol: str):
    # Temporary AI logic
    signal = "HOLD"

    return {
        "symbol": symbol.upper(),
        "signal": signal,
        "entry": None,
        "target": None,
        "stop_loss": None,
        "confidence": 50,
        "strategy": "Basic AI v1"
    }