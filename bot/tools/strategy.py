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
symbols = settings.SYMBOLS
interval = settings.INTERVAL  # 5m execution
adx_period = settings.ADX_PERIOD


def fetch_klines_with_interval(symbol, interval):
    """Fetch klines for a specific symbol and interval."""
    df = fetch_btcusdt_klines(symbol, interval)
    if df.empty:
        loggs.system_log.warning(f"No data fetched for {symbol} on {interval} timeframe.")
    return df


def calculate_indicators(symbol):
    """Calculate indicators for 5m and 15m timeframes."""
    importlib.reload(settings)

    # Fetch 5m and 15m data
    df_5m = fetch_klines_with_interval(symbol, interval)
    df_15m = fetch_klines_with_interval(symbol, '15m')

    if df_5m.empty or df_15m.empty:
        return None, None

    # Calculate EMAs
    for df in [df_5m, df_15m]:
        df['short_ema'] = df['close'].ewm(span=int(settings.SHORT_EMA), adjust=False).mean()
        df['long_ema'] = df['close'].ewm(span=int(settings.LONG_EMA), adjust=False).mean()

    # Calculate RSI
    df_5m['rsi'] = ta.momentum.RSIIndicator(df_5m['close']).rsi()
    df_15m['rsi'] = ta.momentum.RSIIndicator(df_15m['close']).rsi()

    # Calculate ATR
    df_5m['atr'] = ta.volatility.AverageTrueRange(df_5m['high'], df_5m['low'], df_5m['close']).average_true_range()
    df_15m['atr'] = ta.volatility.AverageTrueRange(df_15m['high'], df_15m['low'], df_15m['close']).average_true_range()

    # Calculate ADX
    df_5m['adx'] = ta.trend.ADXIndicator(df_5m['high'], df_5m['low'], df_5m['close']).adx()
    df_15m['adx'] = ta.trend.ADXIndicator(df_15m['high'], df_15m['low'], df_15m['close']).adx()

    return df_5m, df_15m


def detect_breakout(symbol, volume_threshold=1.5):
    """Detect breakout when the price closes above resistance or below support with high volume and confirm with 15m trend."""
    df_5m, df_15m = calculate_indicators(symbol)

    if df_5m is None or df_15m is None:
        return None

    df_5m['resistance'] = df_5m['high'].rolling(window=20).max().shift(1)
    df_5m['support'] = df_5m['low'].rolling(window=20).min().shift(1)
    df_5m['prev_resistance'] = df_5m['resistance'].shift(1)
    df_5m['prev_support'] = df_5m['support'].shift(1)
    df_5m['volume'] = pd.to_numeric(df_5m['volume'], errors='coerce')

    df_5m['breakout_up'] = (df_5m['close'] > df_5m['prev_resistance']) & (
                df_5m['volume'] > df_5m['volume'].rolling(20).mean() * volume_threshold)
    df_5m['breakout_down'] = (df_5m['close'] < df_5m['prev_support']) & (
                df_5m['volume'] > df_5m['volume'].rolling(20).mean() * volume_threshold)

    # Confirm breakout with 15m trend
    is_15m_uptrend = df_15m['short_ema'].iloc[-1] > df_15m['long_ema'].iloc[-1]
    is_15m_downtrend = df_15m['short_ema'].iloc[-1] < df_15m['long_ema'].iloc[-1]

    df_5m['breakout_up'] &= is_15m_uptrend
    df_5m['breakout_down'] &= is_15m_downtrend

    return df_5m


def check_crossover(symbol):
    """Check for trade signals with 15m trend confirmation and breakout strategy."""
    df_5m, df_15m = calculate_indicators(symbol)
    breakout_data = detect_breakout(symbol)

    if df_5m is None or breakout_data is None:
        return [symbol, 'Hold', None, None, None, None, None, None, None]

    prev_short, prev_long = df_5m['short_ema'].iloc[-2], df_5m['long_ema'].iloc[-2]
    curr_short, curr_long = df_5m['short_ema'].iloc[-1], df_5m['long_ema'].iloc[-1]
    curr_price = df_5m['close'].iloc[-1]

    is_15m_uptrend = df_15m['short_ema'].iloc[-1] > df_15m['long_ema'].iloc[-1]
    is_15m_downtrend = df_15m['short_ema'].iloc[-1] < df_15m['long_ema'].iloc[-1]

    crossover_buy = curr_short > curr_long and prev_short < prev_long and is_15m_uptrend
    crossover_sell = curr_short < curr_long and prev_short > prev_long and is_15m_downtrend

    breakout_up = breakout_data['breakout_up'].iloc[-1]
    breakout_down = breakout_data['breakout_down'].iloc[-1]

    if (crossover_buy and df_5m['adx'].iloc[-1]) or (breakout_up and df_5m['adx'].iloc[-1] > 25) :
        return [symbol, 'long', curr_price, df_5m['adx'].iloc[-1], df_5m['atr'].iloc[-1], df_5m['rsi'].iloc[-1],
                curr_long, curr_short, df_5m['volume'].iloc[-1]]
    elif (crossover_sell and df_5m['adx'].iloc[-1]) or (breakout_down and df_5m['adx'].iloc[-1] > 25):
        return [symbol, 'short', curr_price, df_5m['adx'].iloc[-1], df_5m['atr'].iloc[-1], df_5m['rsi'].iloc[-1],
                curr_long, curr_short, df_5m['volume'].iloc[-1]]
    else:
        return [symbol, 'Hold', curr_price, df_5m['adx'].iloc[-1], df_5m['atr'].iloc[-1], df_5m['rsi'].iloc[-1],
                curr_long, curr_short, df_5m['volume'].iloc[-1]]


