import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from binance.client import Client

# Set up the Binance client
API_KEY = 'your_api_key'  # Replace with your Binance API Key
API_SECRET = 'your_api_secret'  # Replace with your Binance API Secret
client = Client(API_KEY, API_SECRET)

# Fetch historical price data for a trading pair (e.g., MATICUSDT)
symbol = 'BTCUSDT'
interval = '5m'  # Hourly candlesticks
lookback = '100 hours ago UTC'

# Get historical candlestick data
candles = client.futures_klines(symbol=symbol, interval=interval, limit=100)
data = pd.DataFrame(candles, columns=['Open Time', 'Open', 'High', 'Low', 'Close', 'Volume',
                                       'Close Time', 'Quote Asset Volume', 'Number of Trades',
                                       'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'])
data['Close'] = data['Close'].astype(float)

# Calculate RSI
def calculate_rsi(data, period=14):
    delta = data['Close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    print(f'RSI: {rsi.iloc[-1]}, {rsi.iloc[-2]}')
    return rsi

data['RSI'] = calculate_rsi(data)

# Calculate SMA of RSI
def calculate_sma(data, period=14):
    return data['RSI'].rolling(window=period).mean()




data['RSI_SMA'] = calculate_sma(data)

# Print last few rows of the data
print(data.tail())
print(data['RSI_SMA'].iloc[-1])
print(data['RSI'].iloc[-1])

# Plot the closing price and RSI with SMA
plt.figure(figsize=(14, 7))

# Price chart
plt.subplot(3, 1, 1)
plt.plot(data['Close'], label='MATIC/USDT Closing Price', color='blue')
plt.title('Price Chart')
plt.ylabel('Price (USDT)')
plt.legend()
plt.grid()

# RSI chart
plt.subplot(3, 1, 2)
plt.plot(data['RSI'], label='RSI', color='orange')
plt.axhline(y=30, color='green', linestyle='--', label='Oversold (30)')
plt.axhline(y=70, color='red', linestyle='--', label='Overbought (70)')
plt.title('RSI Chart')
plt.ylabel('RSI')
plt.legend()
plt.grid()

# SMA of RSI chart
plt.subplot(3, 1, 3)
plt.plot(data['RSI_SMA'], label='SMA of RSI', color='purple')
plt.title('SMA of RSI Chart')
plt.ylabel('SMA of RSI')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
