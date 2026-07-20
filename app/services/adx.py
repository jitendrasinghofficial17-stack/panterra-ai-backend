import pandas as pd
import numpy as np


def calculate_adx(df, period=14):
    """
    Calculate ADX (Average Directional Index)
    """

    df = df.copy()

    high = df["high"]
    low = df["low"]
    close = df["close"]

    # True Range
    df["TR"] = pd.concat([
        high - low,
        (high - close.shift()).abs(),
        (low - close.shift()).abs()
    ], axis=1).max(axis=1)

    # Directional Movement
    plus_dm = high.diff()
    minus_dm = -low.diff()

    plus_dm = np.where(
        (plus_dm > minus_dm) & (plus_dm > 0),
        plus_dm,
        0
    )

    minus_dm = np.where(
        (minus_dm > plus_dm) & (minus_dm > 0),
        minus_dm,
        0
    )

    # ATR
    atr = df["TR"].rolling(period).mean()

    plus_di = (
        100 *
        pd.Series(plus_dm, index=df.index).rolling(period).mean()
        / atr
    )

    minus_di = (
        100 *
        pd.Series(minus_dm, index=df.index).rolling(period).mean()
        / atr
    )

    dx = (
        abs(plus_di - minus_di)
        /
        (plus_di + minus_di)
    ) * 100

    adx = dx.rolling(period).mean()

    df["PLUS_DI"] = plus_di
    df["MINUS_DI"] = minus_di
    df["ADX"] = adx

    return df