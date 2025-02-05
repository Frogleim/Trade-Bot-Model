import pandas as pd
import numpy as np
from binance.client import Client
import ta  # Technical Analysis library

# Binance API keys (Use environment variables for security)
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

# Initialize Binance Client
client = Client(API_KEY, API_SECRET)


# Fetch historical data from Binance Futures
def get_futures_data(symbol="BTCUSDT", interval="15m", limit=100):
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                       'close_time', 'qav', 'trades', 'taker_base', 'taker_quote', 'ignore'])
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype(float)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df


# Detect market conditions (sideways, buy, sell)
def detect_signals(df, adx_threshold=20):
    df['ADX'] = ta.trend.adx(df['high'], df['low'], df['close'], window=14)
    df['RSI'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()

    # Conditions for sideways market
    df['sideways'] = (df['ADX'] < adx_threshold) & (df['RSI'].between(40, 60))

    # Buy signal (RSI below 30 and ADX above 25 for a strong trend)
    df['buy_signal'] = (df['RSI'] < 30) & (df['ADX'] > 25)

    # Sell signal (RSI above 70 and ADX above 25 for a strong trend)
    df['sell_signal'] = (df['RSI'] > 70) & (df['ADX'] > 25)

    return df[['timestamp', 'close', 'ADX', 'RSI', 'sideways', 'buy_signal', 'sell_signal']]


# Run signal detection
def run():
    df = get_futures_data()
    df = detect_signals(df)
    last_signal = df.iloc[-1]  # Get the last row with all signals
    return {
        "sideways": last_signal['sideways'],
        "buy_signal": last_signal['buy_signal'],
        "sell_signal": last_signal['sell_signal']
    }

# Example of how to use the run function:
if __name__ == "__main__":
    signals = run()
    print(signals)  # Output will show if there's a buy or sell signal