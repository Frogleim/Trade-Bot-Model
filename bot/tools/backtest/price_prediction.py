# Import necessary libraries
import pandas as pd
import numpy as np
from binance.client import Client
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

# Step 1: Initialize Binance Client
# Note: No API keys are required for public historical data
client = Client()

# Step 2: Fetch Historical Futures Data
# Fetch 1-hour klines for BTCUSDT perpetual futures from Jan 1, 2020 to Jan 1, 2021
klines = client.futures_historical_klines(
    symbol="BTCUSDT",
    interval=Client.KLINE_INTERVAL_1HOUR,
    start_str="1 Jan, 2020",
    end_str="1 Jan, 2025"
)

# Step 3: Convert Data to DataFrame
# Extract relevant columns and set timestamp as index
df = pd.DataFrame(klines, columns=[
    'timestamp', 'open', 'high', 'low', 'close', 'volume',
    'close_time', 'quote_asset_volume', 'number_of_trades',
    'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)
df = df[['close']].astype(float)  # Use only the closing price for simplicity

# Step 4: Feature Engineering
# Create lagged features (past 24 hours) and target (next hour's close)
for i in range(1, 25):
    df[f'close_t-{i}'] = df['close'].shift(i)  # Lagged closing prices
df['target'] = df['close'].shift(-1)  # Next hour's closing price as target

# Drop rows with NaN values (due to shifting)
df.dropna(inplace=True)

# Step 5: Split Data into Training and Testing Sets
# Use first 80% for training, last 20% for testing (time-series split)
train_size = int(len(df) * 0.8)
train_df = df.iloc[:train_size]
test_df = df.iloc[train_size:]

# Separate features (X) and target (y)
X_train = train_df.drop('target', axis=1)
y_train = train_df['target']
X_test = test_df.drop('target', axis=1)
y_test = test_df['target']

# Step 6: Train the Machine Learning Model
# Use Linear Regression as a simple ML model
model = LinearRegression()
model.fit(X_train, y_train)

# Step 7: Make Predictions
y_pred = model.predict(X_test)

# Step 8: Evaluate the Model
# Calculate Mean Squared Error
mse = mean_squared_error(y_test, y_pred)
print(f'Mean Squared Error: {mse}')

# Step 9: Visualize Results
# Plot actual vs predicted prices
plt.figure(figsize=(12, 6))
plt.plot(y_test.index, y_test, label='Actual Price', color='blue')
plt.plot(y_test.index, y_pred, label='Predicted Price', color='orange')
plt.title('BTCUSDT Futures Price Prediction (1-Hour Interval)')
plt.xlabel('Time')
plt.ylabel('Price (USDT)')
plt.legend()
plt.grid(True)
plt.show()