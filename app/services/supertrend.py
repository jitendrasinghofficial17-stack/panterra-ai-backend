import pandas as pd
import numpy as np


def calculate_supertrend(df, period=10, multiplier=3):
    """
    Calculate Supertrend Indicator

    Returns:
        DataFrame with:
        - ATR
        - Supertrend
        - Supertrend_Direction
    """

    df = df.copy()

    # True Range
    df["previous_close"] = df["close"].shift(1)

    tr1 = df["high"] - df["low"]
    tr2 = (df["high"] - df["previous_close"]).abs()
    tr3 = (df["low"] - df["previous_close"]).abs()

    df["TR"] = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    # ATR
    df["ATR"] = df["TR"].rolling(period).mean()

    # HL2
    hl2 = (df["high"] + df["low"]) / 2

    # Basic Bands
    df["UpperBand"] = hl2 + (multiplier * df["ATR"])
    df["LowerBand"] = hl2 - (multiplier * df["ATR"])

    # Final Bands
    final_upper = df["UpperBand"].copy()
    final_lower = df["LowerBand"].copy()

    for i in range(1, len(df)):

        if (
            final_upper.iloc[i] > final_upper.iloc[i - 1]
            and df["close"].iloc[i - 1] <= final_upper.iloc[i - 1]
        ):
            final_upper.iloc[i] = final_upper.iloc[i - 1]

        if (
            final_lower.iloc[i] < final_lower.iloc[i - 1]
            and df["close"].iloc[i - 1] >= final_lower.iloc[i - 1]
        ):
            final_lower.iloc[i] = final_lower.iloc[i - 1]

    # Supertrend
    supertrend = np.zeros(len(df))
    direction = [""] * len(df)

    for i in range(period, len(df)):

        if i == period:
            supertrend[i] = final_upper.iloc[i]
            direction[i] = "SELL"
            continue

        previous_st = supertrend[i - 1]

        if previous_st == final_upper.iloc[i - 1]:

            if df["close"].iloc[i] <= final_upper.iloc[i]:
                supertrend[i] = final_upper.iloc[i]
                direction[i] = "SELL"
            else:
                supertrend[i] = final_lower.iloc[i]
                direction[i] = "BUY"

        else:

            if df["close"].iloc[i] >= final_lower.iloc[i]:
                supertrend[i] = final_lower.iloc[i]
                direction[i] = "BUY"
            else:
                supertrend[i] = final_upper.iloc[i]
                direction[i] = "SELL"

    df["Supertrend"] = supertrend
    df["Supertrend_Direction"] = direction

    return df