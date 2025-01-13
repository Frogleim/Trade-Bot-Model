import os
from dotenv import load_dotenv
import logging
import pandas as pd
from binance.client import Client
import ta  # Technical Analysis Library
import loggs
from collections import defaultdict
from datetime import datetime, timedelta
import time

# Load environment variables
load_dotenv(dotenv_path='.env')
loggs.system_log.info('Loading .env file')
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

# Initialize Binance Client
client = Client(api_key, api_secret)

# Constants
interval = '15m'
cryptos = ["btcusdt", "ethusdt", "bnbusdt", "adausdt", "xrpusdt"]
data = defaultdict(list)  # To store kline data

# Function to calculate support and resistance levels
def calculate_support_resistance(df):
    """Calculate support and resistance levels."""
    recent_lows = df['low'].rolling(window=20).min()
    recent_highs = df['high'].rolling(window=20).max()
    support = recent_lows.iloc[-1]  # Current support level
    resistance = recent_highs.iloc[-1]  # Current resistance level
    return support, resistance

# Function to calculate EMA, ATR, and support/resistance levels
def calculate_ema_and_sr(df):
    if df.empty:
        return None, None, None, None, None, None, None

    short_ema = df['close'].ewm(span=int(7), adjust=False).mean().iloc[-1]
    long_ema = df['close'].ewm(span=int(14), adjust=False).mean().iloc[-1]
    atr = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=int(14)).iloc[-1]
    support, resistance = calculate_support_resistance(df)
    current_price = df['close'].iloc[-1]
    rejection_type = check_price_rejection(current_price, support, resistance)
    return current_price, atr, support, resistance, short_ema, long_ema, rejection_type

# Function to check price rejection at support or resistance
def check_price_rejection(current_price, support, resistance, tolerance=0.002):
    if abs(current_price - support) / support <= tolerance:
        loggs.system_log.info(f'Price rejected at support level: {support}')
        return 'Support Rejection'
    elif abs(current_price - resistance) / resistance <= tolerance:
        loggs.system_log.info(f'Price rejected at resistance level: {resistance}')
        return 'Resistance Rejection'
    return None

# Function to fetch Kline data from Binance API
def fetch_klines(symbol, interval, limit=50):
    klines = client.get_klines(symbol=symbol.upper(), interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'trades', 'taker_buy_base', 'taker_buy_quote', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]

# Function to process signals
def process_signals(symbol, interval):
    df = fetch_klines(symbol, interval)

    # Perform signal calculation
    current_price, atr, support, resistance, short_ema, long_ema, rejection_type = calculate_ema_and_sr(df)
    if rejection_type == 'Support Rejection' and short_ema > long_ema:
        signal = ['Long', current_price, support, resistance]
        loggs.system_log.info(f'{symbol.upper()}: Long entry signal at {current_price}. Support: {support}, Resistance: {resistance}.')
        return signal
    elif rejection_type == 'Resistance Rejection' and short_ema < long_ema:
        signal = ['Short', current_price, support, resistance]
        loggs.system_log.info(f'{symbol.upper()}: Short entry signal at {current_price}. Support: {support}, Resistance: {resistance}.')
        return signal
    else:
        signal = ['Hold', current_price, support, resistance]
        loggs.system_log.info(f'{symbol.upper()}: Hold signal. Price: {current_price}, Support: {support}, Resistance: {resistance}.')
        return signal


# Function to start fetching data periodically
def start_binance_rest(symbols, interval):
    loggs.system_log.info("Starting REST API fetching for all symbols.")
    try:
        while True:
            for symbol in symbols:
                process_signals(symbol, interval)
            time.sleep(60 * 15)  # Wait for the interval period (15 minutes)
    except KeyboardInterrupt:
        loggs.system_log.warning("Stopped REST API fetching.")
        print("Stopped REST API fetching.")

if __name__ == '__main__':
    start_binance_rest(cryptos, interval)
