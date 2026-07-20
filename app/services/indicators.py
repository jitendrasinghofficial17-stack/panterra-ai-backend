import pandas as pd


def calculate_sma(data, period=20):
    """Simple Moving Average"""
    return data["close"].rolling(period).mean()


def calculate_ema(data, period=20):
    """Exponential Moving Average"""
    return data["close"].ewm(span=period, adjust=False).mean()


def calculate_rsi(data, period=14):
    """Relative Strength Index"""

    delta = data["close"].diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_macd(data):
    """MACD"""

    ema12 = data["close"].ewm(span=12, adjust=False).mean()
    ema26 = data["close"].ewm(span=26, adjust=False).mean()

    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()

    return macd, signal


def calculate_indicators(df):
    """
    Calculate all indicators
    """

    df = df.copy()

    df["SMA20"] = calculate_sma(df)
    df["EMA20"] = calculate_ema(df)
    df["RSI"] = calculate_rsi(df)

    macd, signal = calculate_macd(df)

    df["MACD"] = macd
    df["MACD_SIGNAL"] = signal

    return df