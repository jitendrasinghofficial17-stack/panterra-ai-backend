import pandas as pd


def calculate_atr(df, period=14):
    """
    Calculate Average True Range (ATR)
    """

    df = df.copy()

    df["previous_close"] = df["close"].shift(1)

    df["tr1"] = df["high"] - df["low"]
    df["tr2"] = (df["high"] - df["previous_close"]).abs()
    df["tr3"] = (df["low"] - df["previous_close"]).abs()

    df["true_range"] = df[["tr1", "tr2", "tr3"]].max(axis=1)

    df["ATR"] = df["true_range"].rolling(period).mean()

    return df