import pandas as pd


def calculate_volume(df, period=20):
    """
    Calculate Volume Indicators
    """

    df = df.copy()

    # 20-day average volume
    df["Volume_MA20"] = df["volume"].rolling(period).mean()

    # Relative Volume (RVOL)
    df["RVOL"] = df["volume"] / df["Volume_MA20"]

    # Volume Strength
    volume_signal = []

    for _, row in df.iterrows():

        if pd.isna(row["RVOL"]):
            volume_signal.append("UNKNOWN")

        elif row["RVOL"] >= 2:
            volume_signal.append("VERY HIGH")

        elif row["RVOL"] >= 1.5:
            volume_signal.append("HIGH")

        elif row["RVOL"] >= 1:
            volume_signal.append("NORMAL")

        else:
            volume_signal.append("LOW")

    df["Volume_Signal"] = volume_signal

    return df