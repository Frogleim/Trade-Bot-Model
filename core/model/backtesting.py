import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from itertools import product
from tqdm import tqdm

# Plotting the closing price, EMA Crossover, Bollinger Bands, MACD, and RSI
fig, axs = plt.subplots(4, 1, figsize=(12, 18), sharex=True)
data = pd.read_csv('./Indicators.csv')

def calculate_adx(data, window=14):
    high_diff = data['high'].diff()
    low_diff = data['low'].diff()

    plus_dm = pd.Series(np.where((high_diff > low_diff) & (high_diff > 0), high_diff, 0), index=data.index)
    minus_dm = pd.Series(np.where((low_diff > high_diff) & (low_diff > 0), low_diff, 0), index=data.index)

    tr1 = data['high'] - data['low']
    tr2 = abs(data['high'] - data['close'].shift(1))
    tr3 = abs(data['low'] - data['close'].shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    atr = tr.rolling(window=window).mean()

    plus_di = 100 * (plus_dm.rolling(window=window).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=window).mean() / atr)

    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100

    adx = dx.rolling(window=window).mean()

    return adx

# Parameters for optimization
ema_short_periods = [8, 10, 12]
ema_long_periods = [20, 26, 30]
adx_thresholds = [20, 25, 30]
rsi_oversold_thresholds = [35, 40, 45]
rsi_overbought_thresholds = [55, 60, 65]
bollinger_stddevs = [2, 2.5, 3]

initial_wallet_balance = 55  # Initial wallet balance in dollars
optimization_results = []

# Calculate the total number of combinations
total_combinations = len(ema_short_periods) * len(ema_long_periods) * len(adx_thresholds) * len(rsi_oversold_thresholds) * len(rsi_overbought_thresholds) * len(bollinger_stddevs)

# Use tqdm to add a progress bar
for ema_short, ema_long, adx_threshold, rsi_oversold, rsi_overbought, bollinger_std in tqdm(
    product(ema_short_periods, ema_long_periods, adx_thresholds, rsi_oversold_thresholds, rsi_overbought_thresholds, bollinger_stddevs),
    total=total_combinations, desc="Optimizing"
):
    data['ADX'] = calculate_adx(data, window=14)

    data['EMA_short'] = data['close'].ewm(span=ema_short, adjust=False).mean()
    data['EMA_long'] = data['close'].ewm(span=ema_long, adjust=False).mean()
    data['EMA_crossover'] = np.where((data['EMA_short'] > data['EMA_long']) & (data['ADX'] > adx_threshold), 1, -1)

    data['SMA_50'] = data['close'].rolling(window=50).mean()  # 50-period SMA for trend confirmation
    data['SMA'] = data['close'].rolling(window=20).mean()
    data['stddev'] = data['close'].rolling(window=20).std()
    data['Bollinger_upper'] = data['SMA'] + (data['stddev'] * bollinger_std)
    data['Bollinger_lower'] = data['SMA'] - (data['stddev'] * bollinger_std)
    delta = data['close'].diff()

    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()

    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))

    data['returns'] = data['close'].pct_change()

    data['position'] = 0
    wallet_balance = initial_wallet_balance  # Initialize wallet balance

    # Add fixed stop-loss and take-profit percentages
    stop_loss_pct = 0.02  # 2% stop-loss
    take_profit_pct = 0.04  # 4% take-profit

    entry_price = None
    position_size = wallet_balance * 0.1  # Risk only 10% of wallet balance per trade

    for i in range(1, len(data)):
        if data['EMA_crossover'].iloc[i] == 1 and data['ADX'].iloc[i] > adx_threshold and data['RSI'].iloc[i] > rsi_overbought:
            data.at[i, 'position'] = 1
            entry_price = data['close'].iloc[i]
        elif data['EMA_crossover'].iloc[i] == -1 and data['ADX'].iloc[i] > adx_threshold and data['RSI'].iloc[i] < rsi_oversold:
            data.at[i, 'position'] = 0
            entry_price = data['close'].iloc[i]

        # Check for stop-loss or take-profit
        if entry_price is not None:
            if data['close'].iloc[i] <= entry_price * (1 - stop_loss_pct):
                # Calculate loss and update wallet balance
                loss = position_size * stop_loss_pct
                wallet_balance -= loss
                data.at[i, 'position'] = 0  # Exit on stop-loss
                entry_price = None
            elif data['close'].iloc[i] >= entry_price * (1 + take_profit_pct):
                # Calculate profit and update wallet balance
                profit = position_size * take_profit_pct
                wallet_balance += profit
                data.at[i, 'position'] = 0  # Exit on take-profit
                entry_price = None

    data['strategy_returns'] = data['position'].shift(1) * data['returns']

    total_return = wallet_balance - initial_wallet_balance  # Calculate total profit/loss
    win_rate = np.mean(data['strategy_returns'] > 0)
    sharpe_ratio = data['strategy_returns'].mean() / data['strategy_returns'].std() * np.sqrt(252 * 24 * 4)

    optimization_results.append({
        'ema_short': ema_short,
        'ema_long': ema_long,
        'adx_threshold': adx_threshold,
        'rsi_oversold': rsi_oversold,
        'rsi_overbought': rsi_overbought,
        'bollinger_std': bollinger_std,
        'total_return': total_return,
        'final_wallet_balance': wallet_balance,
        'win_rate': win_rate,
        'sharpe_ratio': sharpe_ratio
    })

optimization_results_df = pd.DataFrame(optimization_results)
optimization_results_df.sort_values(by=['sharpe_ratio', 'win_rate', 'total_return'], ascending=False, inplace=True)

print(optimization_results_df.head())
