import pandas as pd
import numpy as np

# Calculate EMA Crossover, Bollinger Bands, MACD, and RSI for the historical data
data = pd.read_csv('./historical_data/BTCUSDT_15m_1 Jan, 2015_1 Jan, 2024.csv')
# EMA Crossover
data['EMA_short'] = data['close'].ewm(span=12, adjust=False).mean()
data['EMA_long'] = data['close'].ewm(span=26, adjust=False).mean()
data['EMA_crossover'] = np.where(data['EMA_short'] > data['EMA_long'], 1, 0)  # 1 for crossover up, 0 for crossover down

# Bollinger Bands
data['SMA'] = data['close'].rolling(window=20).mean()
data['stddev'] = data['close'].rolling(window=20).std()
data['Bollinger_upper'] = data['SMA'] + (data['stddev'] * 2)
data['Bollinger_lower'] = data['SMA'] - (data['stddev'] * 2)

# MACD
data['MACD'] = data['EMA_short'] - data['EMA_long']
data['Signal_line'] = data['MACD'].ewm(span=9, adjust=False).mean()

# RSI
delta = data['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
data['RSI'] = 100 - (100 / (1 + rs))

# Display the first few rows with the calculated indicators
data[['timestamp', 'close', 'EMA_crossover', 'Bollinger_upper', 'Bollinger_lower', 'MACD', 'Signal_line', 'RSI']].head()
df = pd.DataFrame(data)
df.to_csv('Indicators.csv')