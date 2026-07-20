from app.services.prediction import predict_price


def generate_recommendation(df):

    prediction = predict_price(df)

    confidence = prediction["confidence"]
    probability = prediction["success_probability"]

    if confidence >= 85 and probability >= 85:
        action = "STRONG BUY"

    elif confidence >= 70:
        action = "BUY"

    elif confidence >= 50:
        action = "HOLD"

    elif confidence >= 30:
        action = "SELL"

    else:
        action = "STRONG SELL"

    risk = "LOW"

    if confidence < 60:
        risk = "MEDIUM"

    if confidence < 40:
        risk = "HIGH"

    return {
        "action": action,
        "risk": risk,
        "confidence": confidence,
        "probability": probability,
        "targets": {
            "target1": prediction["target1"],
            "target2": prediction["target2"],
            "target3": prediction["target3"]
        },
        "stop_loss": prediction["stop_loss"],
        "risk_reward": prediction["risk_reward"],
        "reasons": prediction["reasons"]
    }