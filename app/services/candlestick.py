import pandas as pd


def calculate_candlestick_patterns(df):
    """
    Detect common candlestick patterns.
    """

    df = df.copy()

    patterns = []

    for i in range(len(df)):

        if i == 0:
            patterns.append("NONE")
            continue

        current = df.iloc[i]
        previous = df.iloc[i - 1]

        open_price = current["open"]
        close_price = current["close"]
        high = current["high"]
        low = current["low"]

        prev_open = previous["open"]
        prev_close = previous["close"]

        body = abs(close_price - open_price)
        candle_range = high - low

        upper_shadow = high - max(open_price, close_price)
        lower_shadow = min(open_price, close_price) - low

        pattern = "NONE"

        # ------------------------
        # DOJI
        # ------------------------
        if candle_range > 0 and body <= candle_range * 0.1:
            pattern = "DOJI"

        # ------------------------
        # HAMMER
        # ------------------------
        elif (
            lower_shadow >= body * 2
            and upper_shadow <= body
            and close_price > open_price
        ):
            pattern = "HAMMER"

        # ------------------------
        # SHOOTING STAR
        # ------------------------
        elif (
            upper_shadow >= body * 2
            and lower_shadow <= body
            and close_price < open_price
        ):
            pattern = "SHOOTING_STAR"

        # ------------------------
        # BULLISH ENGULFING
        # ------------------------
        elif (
            prev_close < prev_open
            and close_price > open_price
            and open_price < prev_close
            and close_price > prev_open
        ):
            pattern = "BULLISH_ENGULFING"

        # ------------------------
        # BEARISH ENGULFING
        # ------------------------
        elif (
            prev_close > prev_open
            and close_price < open_price
            and open_price > prev_close
            and close_price < prev_open
        ):
            pattern = "BEARISH_ENGULFING"

        # ------------------------
        # BULLISH HARAMI
        # ------------------------
        elif (
            prev_close < prev_open
            and close_price > open_price
            and open_price > prev_close
            and close_price < prev_open
        ):
            pattern = "BULLISH_HARAMI"

        # ------------------------
        # BEARISH HARAMI
        # ------------------------
        elif (
            prev_close > prev_open
            and close_price < open_price
            and open_price < prev_close
            and close_price > prev_open
        ):
            pattern = "BEARISH_HARAMI"

        patterns.append(pattern)

    df["Candlestick"] = patterns

    return df