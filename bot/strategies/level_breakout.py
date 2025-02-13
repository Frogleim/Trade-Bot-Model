import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests


def fetch_binance_data(symbol="BTCUSDT", interval="1h", limit=500):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url).json()
    df = pd.DataFrame(response, columns=["time", "open", "high", "low", "close", "volume",
                                         "close_time", "quote_asset_volume", "trades",
                                         "taker_buy_base", "taker_buy_quote", "ignore"])
    df = df[["time", "open", "high", "low", "close", "volume"]].astype(float)
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df


def identify_levels(df, window=20):
    """Identify local support and resistance levels using rolling min/max"""
    df['resistance'] = df['high'].rolling(window=window).max().shift(1)
    df['support'] = df['low'].rolling(window=window).min().shift(1)
    return df


def detect_breakout(df, volume_threshold=1.5):
    """Detect breakout when the price closes above resistance or below support with high volume"""
    df["prev_resistance"] = df["resistance"].shift(1)
    df["prev_support"] = df["support"].shift(1)

    df["breakout_up"] = (df["close"] > df["prev_resistance"]) & (
                df["volume"] > df["volume"].rolling(20).mean() * volume_threshold)
    df["breakout_down"] = (df["close"] < df["prev_support"]) & (
                df["volume"] > df["volume"].rolling(20).mean() * volume_threshold)

    return df


def backtest_strategy(df, initial_balance=1000, risk_reward_ratio=3):
    balance = initial_balance
    position = 0
    trades = []

    for i in range(1, len(df)):
        if df["breakout_up"].iloc[i]:
            entry_price = df["close"].iloc[i]
            stop_loss = df["support"].iloc[i]
            take_profit = entry_price + (entry_price - stop_loss) * risk_reward_ratio
            position = 1  # Long
            trades.append({"type": "BUY", "entry": entry_price, "stop_loss": stop_loss, "take_profit": take_profit})

        elif df["breakout_down"].iloc[i]:
            entry_price = df["close"].iloc[i]
            stop_loss = df["resistance"].iloc[i]
            take_profit = entry_price - (stop_loss - entry_price) * risk_reward_ratio
            position = -1  # Short
            trades.append({"type": "SELL", "entry": entry_price, "stop_loss": stop_loss, "take_profit": take_profit})

    return trades


# Fetch data
df = fetch_binance_data()

# Identify support and resistance levels
df = identify_levels(df)

# Detect breakouts
df = detect_breakout(df)

# Backtest strategy
trades = backtest_strategy(df)

# Show results
for trade in trades:
    print(trade)