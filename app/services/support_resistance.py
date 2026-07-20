import pandas as pd


def calculate_support_resistance(df, period=20):

    recent = df.tail(period)

    support = round(recent["low"].min(), 2)
    resistance = round(recent["high"].max(), 2)

    return {
        "support": support,
        "resistance": resistance
    }