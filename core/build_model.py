import pandas as pd
from binance.client import Client
import numpy as np
import config
# Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'
symbol = 'ETHUSDT'  # Example: BTCUSDT

# Initialize Binance API
client = Client(config.API_KEY, config.API_SECRET)

# Function to fetch historical klines (candlestick) data
def fetch_klines(symbol, interval, limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    return df

# Function to implement Moving Average Crossover strategy
def ma_crossover_strategy(df, short_window, long_window):
    signals = pd.DataFrame(index=df.index)
    signals['signal'] = 0.0

    # Create short simple moving average
    signals['short_mavg'] = df['close'].rolling(window=short_window, min_periods=1, center=False).mean()

    # Create long simple moving average
    signals['long_mavg'] = df['close'].rolling(window=long_window, min_periods=1, center=False).mean()

    # Create signals
    signals['signal'][short_window:] = np.where(signals['short_mavg'][short_window:] > signals['long_mavg'][short_window:], 1.0, 0.0)

    # Generate trading orders
    signals['positions'] = signals['signal'].diff()

    return signals

# Example parameters
short_window = 50
long_window = 200
interval = '1h'  # 1-hour interval

# Fetch historical klines data
historical_data = fetch_klines(symbol, interval)

# Implement strategy
signals = ma_crossover_strategy(historical_data, short_window, long_window)

# Print the signals
print(signals)
