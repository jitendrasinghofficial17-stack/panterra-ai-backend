import pandas as pd


def calculate_bollinger_bands(df, period=20, std_dev=2):
    """
    Calculate Bollinger Bands
    """

    df = df.copy()

    # Middle Band (20 SMA)
    df["BB_MIDDLE"] = df["close"].rolling(period).mean()

    # Standard Deviation
    rolling_std = df["close"].rolling(period).std()

    # Upper & Lower Bands
    df["BB_UPPER"] = df["BB_MIDDLE"] + (rolling_std * std_dev)
    df["BB_LOWER"] = df["BB_MIDDLE"] - (rolling_std * std_dev)

    # Band Width
    df["BB_WIDTH"] = (
        (df["BB_UPPER"] - df["BB_LOWER"])
        / df["BB_MIDDLE"]
    ) * 100

    # Position of Price
    signal = []

    for _, row in df.iterrows():

        if pd.isna(row["BB_UPPER"]):
            signal.append("UNKNOWN")

        elif row["close"] > row["BB_UPPER"]:
            signal.append("OVERBOUGHT")

        elif row["close"] < row["BB_LOWER"]:
            signal.append("OVERSOLD")

        else:
            signal.append("NORMAL")

    df["BB_SIGNAL"] = signal

    return df