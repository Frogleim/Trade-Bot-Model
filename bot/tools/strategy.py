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
symbols = settings.SYMBOLS  # Update settings to include a list of symbols
interval = settings.INTERVAL
adx_period = settings.ADX_PERIOD


def calculate_ema(symbol):
    """Calculating indicators for fast execution scalping strategy for a given symbol"""
    importlib.reload(settings)

    df = fetch_btcusdt_klines(symbol, interval)
    if df.empty:
        print(f"No data fetched for {symbol}.")
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
        f'{symbol} - Long EMA: {long_ema.iloc[-1]} Short EMA: {short_ema.iloc[-1]} ATR: {atr} ADX: {adx.iloc[-1]} '
        f'RSI: {rsi.iloc[-1]} Volume: {volume.iloc[-1]}')

    return long_ema, short_ema, df['close'], adx, atr, rsi, volume


def identify_levels(df, window=20):
    """Identify local support and resistance levels using rolling min/max"""
    df['resistance'] = df['high'].rolling(window=window).max().shift(1)
    df['support'] = df['low'].rolling(window=window).min().shift(1)
    return df


def detect_breakout(symbol, volume_threshold=1.5):

    """Detect breakout when the price closes above resistance or below support with high volume"""
    df = fetch_btcusdt_klines(symbol, interval)

    df['resistance'] = df['high'].rolling(window=20).max().shift(1)
    df['support'] = df['low'].rolling(window=20).min().shift(1)
    df["prev_resistance"] = df["resistance"].shift(1)
    df["prev_support"] = df["support"].shift(1)
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")  # Convert to float, coerce errors to NaN

    df["breakout_up"] = (df["close"] > df["prev_resistance"]) & (
                df["volume"] > df["volume"].rolling(20).mean() * volume_threshold)
    df["breakout_down"] = (df["close"] < df["prev_support"]) & (
                df["volume"] > df["volume"].rolling(20).mean() * volume_threshold)

    return df


def check_crossover(symbol):
    """Scalping-based trade signal strategy with risk management for a given symbol"""
    importlib.reload(settings)
    long_ema, short_ema, close_price_series, adx, atr, rsi, volume = calculate_ema(symbol)

    def safe_convert(series):
        return pd.to_numeric(series, errors='coerce') if series is not None else None

    long_ema = safe_convert(long_ema)
    short_ema = safe_convert(short_ema)
    close_price_series = safe_convert(close_price_series)
    adx = safe_convert(adx)
    atr = float(atr) if atr is not None else None
    rsi = safe_convert(rsi)
    volume = safe_convert(volume)

    if any(data is None or isinstance(data, pd.Series) and data.isnull().all() for data in
           [short_ema, long_ema, close_price_series, adx, atr, rsi, volume]):
        loggs.system_log.error(f"{symbol} - Missing or invalid data. Skipping crossover check.")
        return [symbol, 'Hold', None, None, None, None, None, None, None]

    prev_short, prev_long = short_ema.iloc[-2], long_ema.iloc[-2]
    curr_short, curr_long = short_ema.iloc[-1], long_ema.iloc[-1]
    prev_price, curr_price = close_price_series.iloc[-2], close_price_series.iloc[-1]

    if any(pd.isna(val) for val in [prev_short, prev_long, curr_short, curr_long, prev_price, curr_price]):
        loggs.system_log.error(f"{symbol} - NaN values detected. Skipping crossover check.")
        return [symbol, 'Hold', None, None, None, None, None, None, None]

    crossover_buy = curr_short > curr_long and prev_short < prev_long
    rsi_buy = 45 < rsi.iloc[-1] < 65
    strong_trend = adx.iloc[-1] > 25
    valid_atr = atr > 0.05 * curr_price
    volume_avg = volume.rolling(window=14).mean().iloc[-1]
    high_volume = volume.iloc[-1] > volume_avg * 1.2

    crossover_sell = curr_short < curr_long and prev_short > prev_long
    rsi_sell = 35 < rsi.iloc[-1] < 55
    strong_trend_sell = adx.iloc[-1] > 25
    valid_atr_sell = atr > 0.05 * curr_price
    high_volume_sell = volume.iloc[-1] > volume_avg * 1.2

    loggs.system_log.info(
        f"{symbol} - ADX: {adx.iloc[-1]}, ATR: {atr}, Volume: {volume.iloc[-1]}, "
        f"Crossover Buy: {crossover_buy}, Crossover Sell: {crossover_sell}, "
        f"RSI Buy: {rsi_buy}, RSI Sell: {rsi_sell}, "
        f"Valid ATR: {valid_atr}, High Volume: {high_volume}"
    )
    loggs.debug_log.debug(
        f"Symbol: {symbol} Current Price: {curr_price}, Volume: {volume.iloc[-1]}, adx: {adx.iloc[-1]} atr: {atr}, rsi: {rsi.iloc[-1]}, long_ema: {curr_long}, short_ema: {curr_short} "
    )

    is_break_out = detect_breakout(symbol)
    if crossover_buy and strong_trend or (is_break_out['breakout_up'].iloc[-1] and strong_trend):
        return [symbol, 'long', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]
    elif crossover_sell and strong_trend_sell or (is_break_out['breakout_down'].iloc[-1] and strong_trend_sell):
        return [symbol, 'short', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]
    else:
        return [symbol, 'Hold', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]



def monitor_cryptos():
    """Monitor signals for multiple cryptocurrencies"""
    results = []
    for symbol in symbols:
        result = check_crossover(symbol)
        results.append(result)

    df_results = pd.DataFrame(results,
                              columns=['Symbol', 'Signal', 'Price', 'ADX', 'ATR', 'RSI', 'Long EMA', 'Short EMA',
                                       'Volume'])
    print(df_results)
    return df_results


if __name__ == '__main__':
    monitor_cryptos()