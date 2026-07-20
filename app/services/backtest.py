from app.services.market_data import get_historical_data
from app.services.indicators import calculate_indicators
from app.services.supertrend import calculate_supertrend
from app.services.adx import calculate_adx
from app.services.bollinger import calculate_bollinger_bands
from app.services.volume import calculate_volume
from app.services.candlestick import calculate_candlestick_patterns


def backtest(symbol: str):

    df = get_historical_data(symbol)

    if df is None or df.empty:
        return None

    df = calculate_indicators(df)
    df = calculate_supertrend(df)
    df = calculate_adx(df)
    df = calculate_bollinger_bands(df)
    df = calculate_volume(df)
    df = calculate_candlestick_patterns(df)

    trades = []

    position = None

    for i in range(30, len(df)):

        row = df.iloc[i]

        buy = (
            row["Supertrend_Direction"] == "BUY"
            and row["MACD"] > row["MACD_SIGNAL"]
            and row["RSI"] > 55
        )

        sell = (
            row["Supertrend_Direction"] == "SELL"
            and row["MACD"] < row["MACD_SIGNAL"]
            and row["RSI"] < 45
        )

        if position is None and buy:

            position = row["close"]

        elif position is not None and sell:

            pnl = row["close"] - position

            trades.append(pnl)

            position = None

    return trades