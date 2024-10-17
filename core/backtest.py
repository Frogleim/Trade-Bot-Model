import pandas as pd
import talib
import matplotlib.pyplot as plt
import requests

def get_binance_futures_data(symbol, interval, limit=500):
    url = (f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}"
           f"&interval={interval}&limit={limit}")
    data = requests.get(url).json()
    df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time',
                                     'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['close'] = df['close'].astype(float)
    return df[['timestamp', 'close']]

symbol = 'BTCUSDT'
interval = '5m'
df = get_binance_futures_data(symbol, interval)

short_ema_period = 5
long_ema_period = 13
df['EMA_12'] = talib.EMA(df['close'], timeperiod=short_ema_period)
df['EMA_26'] = talib.EMA(df['close'], timeperiod=long_ema_period)
df['ADX'] = talib.ADX(df['close'], timeperiod=14)
plt.figure(figsize=(14, 8))
plt.plot(df['timestamp'], df['close'], label='Close Price', color='black', alpha=0.6)
plt.plot(df['timestamp'], df['EMA_12'], label=f'EMA {short_ema_period}', color='blue', linestyle='--')
plt.plot(df['timestamp'], df['EMA_26'], label=f'EMA {long_ema_period}', color='red', linestyle='--')
buy_signals = (df['EMA_12'] > df['EMA_26']) & (df['EMA_12'].shift(1) <= df['EMA_26'].shift(1))
sell_signals = (df['EMA_12'] < df['EMA_26']) & (df['EMA_12'].shift(1) >= df['EMA_26'].shift(1))
plt.plot(df.loc[buy_signals, 'timestamp'],
         df.loc[buy_signals, 'close'], '^', color='green', markersize=10, label='Buy Signal')
plt.plot(df.loc[sell_signals, 'timestamp'],
         df.loc[sell_signals, 'close'], 'v', color='red', markersize=10, label='Sell Signal')
plt.title(f'{symbol} EMA Crossover ({interval})')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
