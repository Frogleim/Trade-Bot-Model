from binance.client import Client
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ta

# Your Binance API credentials
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

# Initialize the Binance client
client = Client(api_key, api_secret)

# Fetch historical futures data
symbol = 'BTCUSDT'
klines = client.futures_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_15MINUTE, start_str='2020-01-01',
                               end_str='2023-01-01')

# Create DataFrame
columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume',
           'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore']
df = pd.DataFrame(klines, columns=columns)
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
df.set_index('timestamp', inplace=True)
df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)

# Calculate Bollinger Bands
bb_indicator = ta.volatility.BollingerBands(close=df['close'], window=20, window_dev=2)
df['bb_mavg'] = bb_indicator.bollinger_mavg()
df['bb_upper'] = bb_indicator.bollinger_hband()
df['bb_lower'] = bb_indicator.bollinger_lband()

# Calculate ADX
adx_indicator = ta.trend.ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
df['adx'] = adx_indicator.adx()

# Define strategy
df['signal'] = np.where((df['close'] < df['bb_lower']) & (df['adx'] > 20), 1, 0)
df['signal'] = np.where((df['close'] > df['bb_upper']) & (df['adx'] > 20), -1, df['signal'])

# Initial capital
initial_capital = 100.0
transaction_cost = 0.001  # 0.1% per transaction

df['position'] = df['signal']  # No need to shift
df['daily_returns'] = df['close'].pct_change()

# Calculate daily portfolio value
df['portfolio_value'] = initial_capital
df['cash'] = initial_capital
df['holdings'] = 0

for i in range(1, len(df)):
    if df['position'].iloc[i] == 1:  # Buy signal
        if df['cash'].iloc[i - 1] > 0:
            holdings = df['cash'].iloc[i - 1] * (1 - transaction_cost) / df['close'].iloc[i]
            df.at[df.index[i], 'holdings'] = holdings
            df.at[df.index[i], 'cash'] = 0
    elif df['position'].iloc[i] == -1:  # Sell signal
        if df['holdings'].iloc[i - 1] > 0:
            cash = df['holdings'].iloc[i - 1] * df['close'].iloc[i] * (1 - transaction_cost)
            df.at[df.index[i], 'cash'] = cash
            df.at[df.index[i], 'holdings'] = 0
    else:  # Hold position
        df.at[df.index[i], 'cash'] = df['cash'].iloc[i - 1]
        df.at[df.index[i], 'holdings'] = df['holdings'].iloc[i - 1]

    df.at[df.index[i], 'portfolio_value'] = df['cash'].iloc[i] + df['holdings'].iloc[i] * df['close'].iloc[i]

# Performance Metrics
df['strategy_returns'] = df['portfolio_value'].pct_change().fillna(0)
cumulative_returns = df['portfolio_value'].iloc[-1] / initial_capital - 1
max_drawdown = (df['portfolio_value'].cummax() - df['portfolio_value']).max() / df['portfolio_value'].cummax().max()
sharpe_ratio = (df['strategy_returns'].mean() / df['strategy_returns'].std()) * np.sqrt(
    252 * (24 * 4))  # Adjusted for 15-min intervals

# Debugging information
print("Debugging Information:")
print(
    df[['close', 'bb_lower', 'bb_upper', 'adx', 'signal', 'position', 'portfolio_value', 'cash', 'holdings']].tail(20))

# Plot results
plt.figure(figsize=(14, 7))
plt.plot(df['portfolio_value'], label='Portfolio Value', color='blue')
plt.title(f'Bollinger Bands and ADX Strategy Backtest with Initial Capital of ${initial_capital}')
plt.xlabel('Date')
plt.ylabel('Portfolio Value')
plt.legend()
plt.grid(True)
plt.show()

# Print performance metrics
print(f"Final Portfolio Value: ${df['portfolio_value'].iloc[-1]:.2f}")
print(f"Cumulative Returns: {cumulative_returns * 100:.2f}%")
print(f"Maximum Drawdown: {max_drawdown * 100:.2f}%")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")