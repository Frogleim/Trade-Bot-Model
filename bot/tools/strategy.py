from .socket_binance import fetch_btcusdt_klines
from binance.client import Client
from . import loggs
from .settings import settings
import ta
from dotenv import load_dotenv
import os
import pandas as pd
import importlib

load_dotenv(dotenv_path='./tools/.env')

client = Client()
symbol = settings.SYMBOL
interval = settings.INTERVAL
lookback = 5
adx_period = settings.ADX_PERIOD

def calculate_ema():
    """Calculating indicators for fast execution scalping strategy"""
    importlib.reload(settings)

    df = fetch_btcusdt_klines(symbol, interval)
    if df.empty:
        print("No data fetched.")
        return None, None, None, None, None, None, None

    # Calculate EMAs
    short_ema = df['close'].ewm(span=int(settings.SHORT_EMA), adjust=False).mean()
    long_ema = df['close'].ewm(span=int(settings.LONG_EMA), adjust=False).mean()

    # Calculate RSI
    df['previous_close'] = df['close'].shift(1)
    delta = df['close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    # Calculate ATR
    atr_period = int(os.getenv('ATR_PERIOD'))
    df['high_low'] = df['high'] - df['low']
    df['high_prev_close'] = abs(df['high'] - df['previous_close'])
    df['low_prev_close'] = abs(df['low'] - df['previous_close'])
    df['true_range'] = df[['high_low', 'high_prev_close', 'low_prev_close']].max(axis=1)
    df['ATR'] = df['true_range'].rolling(window=atr_period).mean()
    atr = df['ATR'].iloc[-1]

    # Calculate ADX
    adx = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)

    # Volume Data
    volume = df['volume']

    loggs.system_log.info(
        f'Long EMA: {long_ema.iloc[-1]} Short EMA: {short_ema.iloc[-1]} ATR: {atr} ADX: {adx.iloc[-1]} '
        f'RSI: {rsi.iloc[-1]} Volume: {volume.iloc[-1]}')

    return long_ema, short_ema, df['close'], adx, atr, rsi, volume


def check_crossover():
    """Scalping-based trade signal strategy with risk management"""
    importlib.reload(settings)

    long_ema, short_ema, close_price_series, adx, atr, rsi, volume = calculate_ema()

    # Ensure valid data
    if any(data is None for data in [long_ema, short_ema, close_price_series, adx, atr, rsi, volume]):
        return ['Hold', None, None, None, None, None, None, None]

    # Extract latest and previous values
    prev_short, prev_long = short_ema.iloc[-2], long_ema.iloc[-2]
    curr_short, curr_long = short_ema.iloc[-1], long_ema.iloc[-1]
    prev_price, curr_price = close_price_series.iloc[-2], close_price_series.iloc[-1]

    # **Scalping Buy Signal:**
    crossover_buy = curr_short > curr_long and prev_short < prev_long  # Golden Cross
    rsi_buy = 45 < rsi.iloc[-1] < 65  # RSI in momentum zone
    strong_trend = adx.iloc[-1] > 25  # Strong ADX
    valid_atr = atr > 0.05 * curr_price  # Ensuring ATR is sufficient
    volume_avg = volume.rolling(window=14).mean().iloc[-1]
    high_volume = volume.iloc[-1] > volume_avg * 1.2  # Volume surge

    # **Scalping Sell Signal:**
    crossover_sell = curr_short < curr_long and prev_short > prev_long  # Death Cross
    rsi_sell = 35 < rsi.iloc[-1] < 55  # RSI in downtrend
    valid_atr_sell = atr > 0.05 * curr_price
    strong_trend_sell = adx.iloc[-1] > 25
    high_volume_sell = volume.iloc[-1] > volume_avg * 1.2

    loggs.system_log.info(
        f"ADX: {adx.iloc[-1]}, ATR: {atr}, Volume: {volume.iloc[-1]}, "
        f"Crossover Buy: {crossover_buy}, Crossover Sell: {crossover_sell}, "
        f"RSI Buy: {rsi_buy}, RSI Sell: {rsi_sell}, "
        f"Valid ATR: {valid_atr}, High Volume: {high_volume}"
    )

    # Entry conditions
    if crossover_buy and strong_trend and rsi_buy and valid_atr and high_volume:
        return ['long', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]
    elif crossover_sell and strong_trend_sell and rsi_sell and valid_atr_sell and high_volume_sell:
        return ['short', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]
    else:
        return ['Hold', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]