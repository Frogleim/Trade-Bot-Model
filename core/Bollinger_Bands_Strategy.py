from binance.client import Client
import pandas as pd
import numpy as np
import config
import matplotlib.pyplot as plt

# Binance API credentials
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(config.API_KEY, config.API_SECRET)


# Function to fetch historical klines data from Binance
def get_historical_data(symbol, interval, limit):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    data = pd.DataFrame(klines, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                                         'Quote asset volume', 'Number of trades', 'Taker buy base asset volume',
                                         'Taker buy quote asset volume', 'Ignore'])
    data['Open time'] = pd.to_datetime(data['Open time'], unit='ms')
    data.set_index('Open time', inplace=True)
    data['Close'] = data['Close'].astype(float)
    return data


# Function to calculate Bollinger Bands
def calculate_bollinger_bands(data, window_size, num_std_dev):
    data['Rolling Mean'] = data['Close'].rolling(window=window_size).mean()
    data['Upper Band'] = data['Rolling Mean'] + (data['Close'].rolling(window=window_size).std() * num_std_dev)
    data['Lower Band'] = data['Rolling Mean'] - (data['Close'].rolling(window=window_size).std() * num_std_dev)
    return data


# Function to implement Bollinger Bands strategy
def implement_bollinger_strategy(data, window_size, num_std_dev):
    data = calculate_bollinger_bands(data, window_size, num_std_dev)

    # Generate signals
    data['Signal'] = 0
    data['Signal'][data['Close'] > data['Upper Band']] = -1  # Sell Signal
    data['Signal'][data['Close'] < data['Lower Band']] = 1  # Buy Signal

    # Calculate daily returns
    data['Daily Return'] = data['Close'].pct_change()

    # Calculate strategy returns
    data['Strategy Return'] = data['Daily Return'] * data['Signal'].shift(1)

    return data


# Main function
if __name__ == "__main__":
    # Define trading parameters
    symbol = 'BTCUSDT'
    interval = '1h'  # 1-hour candles
    limit = 100  # Number of periods to fetch
    window_size = 20
    num_std_dev = 2

    # Fetch historical data
    historical_data = get_historical_data(symbol, interval, limit)

    # Implement Bollinger Bands strategy
    strategy_data = implement_bollinger_strategy(historical_data, window_size, num_std_dev)

    # Visualize Bollinger Bands and signals
    plt.figure(figsize=(12, 6))
    plt.plot(strategy_data['Close'], label='Close Price', linewidth=2)
    plt.plot(strategy_data['Upper Band'], label='Upper Band', linestyle='--', color='red')
    plt.plot(strategy_data['Lower Band'], label='Lower Band', linestyle='--', color='green')
    plt.scatter(strategy_data.index, strategy_data['Close'][strategy_data['Signal'] == 1], marker='^', color='green')
    plt.scatter(strategy_data.index, strategy_data['Close'][strategy_data['Signal'] == -1], marker='v', color='red')
    plt.title('Bollinger Bands Strategy')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()
