import pandas as pd
import numpy as np
from binance.client import Client

# Binance API Keys (replace with your own keys)
API_KEY = 'your_api_key'
API_SECRET = 'your_api_secret'

client = Client(API_KEY, API_SECRET)


def fetch_historical_data(symbol, interval, start_date, end_date):
    """Fetch historical data from Binance Futures and return a DataFrame."""
    klines = client.futures_historical_klines(symbol, interval, start_date, end_date)
    df = pd.DataFrame(klines, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_volume",
        "taker_buy_quote_volume", "ignore"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit='ms')
    df["close"] = df["close"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    return df


def compute_indicators(df):
    """Compute scalping strategy indicators."""
    df['EMA_Short'] = df['close'].ewm(span=3, adjust=False).mean()
    df['EMA_Long'] = df['close'].ewm(span=8, adjust=False).mean()
    df['ATR'] = df['high'].rolling(14).max() - df['low'].rolling(14).min()
    df['ADX'] = abs(df['ATR'].diff()).rolling(14).mean()
    df['RSI'] = 100 - (100 / (1 + df['close'].diff().where(df['close'].diff() > 0, 0).rolling(10).mean() /
                              -df['close'].diff().where(df['close'].diff() < 0, 0).rolling(10).mean()))
    return df


def backtest_strategy(df):
    """Backtest the scalping strategy with $100 price movement per trade."""
    balance = 10000
    position = 0
    entry_price = 0
    trades = []

    for i in range(1, len(df)):
        if position == 0:
            if df.loc[i, 'EMA_Short'] > df.loc[i, 'EMA_Long'] and df.loc[i, 'ADX'] > 25:
                position = 1
                entry_price = df.loc[i, 'close']
                sl = entry_price - 100 
                tp = entry_price + 400  
                trades.append(('Buy', entry_price, df.loc[i, 'timestamp'], balance))
            elif df.loc[i, 'EMA_Short'] < df.loc[i, 'EMA_Long'] and df.loc[i, 'ADX'] > 25:
                position = -1
                entry_price = df.loc[i, 'close']
                sl = entry_price + 100  # SL at $50 above entry price
                tp = entry_price - 400  # TP at $100 below entry price
                trades.append(('Sell', entry_price, df.loc[i, 'timestamp'], balance))
        elif position == 1:
            if df.loc[i, 'close'] >= tp:
                profit = balance * 0.5  # Leverage 125x
                balance += profit
                position = 0
                trades.append(('Sell_Close', df.loc[i, 'close'], df.loc[i, 'timestamp'], profit, balance))
            elif df.loc[i, 'close'] <= sl:
                profit = balance * 0.5  # Leverage 125x
                balance -= profit
                position = 0
                trades.append(('Sell_Close', df.loc[i, 'close'], df.loc[i, 'timestamp'], profit, balance))
        elif position == -1:
            if df.loc[i, 'close'] <= tp:
                profit = balance * 0.5# Leverage 125x
                balance += profit
                position = 0
                trades.append(('Buy_Close', df.loc[i, 'close'], df.loc[i, 'timestamp'], profit, balance))
            elif df.loc[i, 'close'] >= sl:
                profit = balance * 0.5  # Leverage 125x
                balance -= profit
                position = 0
                trades.append(('Buy_Close', df.loc[i, 'close'], df.loc[i, 'timestamp'], profit, balance))

    print(f'Final balance: {balance}')
    trades_df = pd.DataFrame(trades, columns=['Action', 'Price', 'Timestamp', 'Profit', 'Balance']).fillna(0)
    trades_df.to_csv("backtest_results.csv", index=False)
    return trades_df


# Example Usage
df = fetch_historical_data('BTCUSDT', '5m', '2024-01-01', '2024-01-30')
df = compute_indicators(df)
results = backtest_strategy(df)
print("Backtest results saved to backtest_results.csv")
