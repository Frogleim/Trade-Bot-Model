from binance.client import Client
import pandas as pd
import pandas_ta as ta
import matplotlib.pyplot as plt
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import GOOG

# Initialize Binance client (replace with your API key and secret)
client = Client(api_key='your_api_key', api_secret='your_api_secret')

# Get historical data for a specific symbol
def get_historical_data(symbol, interval, start, end):
    klines = client.get_historical_klines(symbol, interval, start, end)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                       'close_time', 'quote_av', 'trades',
                                       'tb_base_av', 'tb_quote_av', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['close'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['open'] = df['open'].astype(float)
    return df

# Example: Fetch historical data for BTCUSDT
data = get_historical_data('ETHUSDT', '1h', '1 Jan 2023', '1 Aug 2023')

# Calculate Indicators using pandas_ta
data['EMA200'] = ta.ema(data['close'], length=200)
data['EMA20'] = ta.ema(data['close'], length=20)
data['EMA50'] = ta.ema(data['close'], length=50)
data['StochRSI'] = ta.stochrsi(data['close'], length=14, rsi_length=14, k=3, d=3)['STOCHRSIk_14_3_3']

# Strategy implementation for backtesting
class TrendFollowingStrategy(Strategy):
    def init(self):
        self.ema200 = self.I(ta.ema, self.data.Close, length=200)
        self.ema20 = self.I(ta.ema, self.data.Close, length=20)
        self.ema50 = self.I(ta.ema, self.data.Close, length=50)
        self.stochrsi = self.I(ta.stochrsi, self.data.Close, length=14, rsi_length=14, k=3, d=3)['STOCHRSIk_14_3_3']

    def next(self):
        if self.data.Close[-1] > self.ema200[-1]:  # Only consider long positions
            if (self.data.Close[-1] < self.ema20[-1] and self.stochrsi[-1] < 20):  # Entry condition for long
                self.buy(sl=self.data.Low[-1] * 0.99, tp=self.data.High[-1] * 1.02)
        elif self.data.Close[-1] < self.ema200[-1]:  # Only consider short positions
            if (self.data.Close[-1] > self.ema20[-1] and self.stochrsi[-1] > 80):  # Entry condition for short
                self.sell(sl=self.data.High[-1] * 1.01, tp=self.data.Low[-1] * 0.98)

# Backtest the strategy
bt = Backtest(data, TrendFollowingStrategy, cash=10000, commission=.002)
stats = bt.run()
bt.plot()

print(stats)
