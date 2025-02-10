from .socket_binance import fetch_btcusdt_klines
from binance.client import Client
from . import loggs
from .settings import settings
import ta
from dotenv import load_dotenv
import os
import pandas as pd
import importlib

loaded = load_dotenv(dotenv_path='./tools/.env')

client = Client()
symbol = settings.SYMBOL
interval = settings.INTERVAL
lookback = 5
adx_period = settings.ADX_PERIOD

def calculate_ema():
    """Calculating indicators including volume"""
    importlib.reload(settings)  # 🔄 Reload settings dynamically

    df = fetch_btcusdt_klines(symbol, interval)
    if df.empty:
        print("No data fetched.")
        return None, None, None, None, None, None

    # Calculate EMAs
    short_ema = df['close'].ewm(span=int(settings.SHORT_EMA), adjust=False).mean()
    long_ema = df['close'].ewm(span=int(settings.LONG_EMA), adjust=False).mean()

    # Calculate RSI
    close_price_series = df['close']
    df['previous_close'] = df['close'].shift(1)
    df['high_low'] = df['high'] - df['low']
    df['high_prev_close'] = abs(df['high'] - df['previous_close'])
    df['low_prev_close'] = abs(df['low'] - df['previous_close'])
    delta = df['close'].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi_sma = rsi.rolling(window=14).mean()

    # Calculate ATR
    df['true_range'] = df[['high_low', 'high_prev_close', 'low_prev_close']].max(axis=1)
    atr_period = int(os.getenv('ATR_PERIOD'))
    df['ATR'] = df['true_range'].rolling(window=atr_period).mean()
    atr = df['ATR'].iloc[-1]

    # Calculate ADX
    adx_period = 14
    adx = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)

    # Get Volume Data
    df['volume'] = df['volume']

    loggs.system_log.info(
        f'Long EMA: {long_ema.iloc[-1]} Short EMA: {short_ema.iloc[-1]} ATR: {df["ATR"].iloc[-2]} ADX: {adx.iloc[-1]}'
        f' RSI: {rsi.iloc[-1]} RSI SMA: {rsi_sma.iloc[-1]} Volume: {df["volume"].iloc[-1]}')

    return long_ema, short_ema, close_price_series, adx, atr, rsi, df['volume']


def check_crossover():
    """Enhanced trade signal strategy with type safety and trend confirmation."""
    importlib.reload(settings)  # 🔄 Reload settings dynamically


    long_ema, short_ema, close_price_series, adx, atr, rsi, volume = calculate_ema()
    loggs.debug_log.debug(
        f'Take profit ATR: {settings.TAKE_PROFIT_ATR} Stop loss ATR: {settings.STOP_LOSS_ATR} ATR: {settings.ATR} {settings.ADX_PERIOD} Short EMA: {settings.SHORT_EMA} Long EMA: {settings.LONG_EMA}')

    # Ensure all values are numeric
    def safe_convert(series):
        return pd.to_numeric(series, errors='coerce') if series is not None else None

    long_ema = safe_convert(long_ema)
    short_ema = safe_convert(short_ema)
    close_price_series = safe_convert(close_price_series)
    adx = safe_convert(adx)
    atr = float(atr) if atr is not None else None
    rsi = safe_convert(rsi)
    volume = safe_convert(volume)

    # Validate required data
    missing_data = {}
    if short_ema is None or len(short_ema) < 2:
        missing_data['short_ema'] = 'Missing or invalid'
    if long_ema is None or len(long_ema) < 2:
        missing_data['long_ema'] = 'Missing or invalid'
    if close_price_series is None:
        missing_data['close_price'] = 'Missing'
    if adx is None or len(adx) == 0 or adx.iloc[-1] is None:
        missing_data['adx'] = 'Missing or invalid'
    if atr is None or float(atr) <= 0:
        missing_data['atr'] = 'Missing or invalid'
    if volume is None or volume.iloc[-1] == 0:
        missing_data['volume'] = 'Missing or invalid'

    if missing_data:
        raise ValueError(f"Missing or invalid data: {missing_data}")

    # Define conditions for crossover
    prev_short, prev_long = short_ema.iloc[-2], long_ema.iloc[-2]
    curr_short, curr_long = short_ema.iloc[-1], long_ema.iloc[-1]
    prev_price, curr_price = close_price_series.iloc[-2], close_price_series.iloc[-1]

    # Bullish crossover (Golden Cross)
    # crossover_buy = (prev_short < prev_long and curr_short > curr_long) and \
    #                 (curr_price > curr_short and curr_price > curr_long)
    crossover_buy = curr_short > curr_long and prev_short > prev_long
    crossover_sell = curr_short < curr_long and prev_short < prev_long
    # Bearish crossover (Death Cross)
    # crossover_sell = (prev_short > prev_long and curr_short < curr_long) and \
    #                  (curr_price < curr_short and curr_price < curr_long)

    # ADX confirms trend strength
    strong_trend = adx.iloc[-1] > 24.66939454890813

    # RSI confirmation
    rsi_long = 45 < rsi.iloc[-1] < 65
    rsi_short = 35 < rsi.iloc[-1] < 55

    # ATR ensures sufficient volatility
    min_atr_threshold = atr * 0.1
    valid_atr = atr > min_atr_threshold

    # Dynamic volume threshold based on moving average
    volume_avg = volume.rolling(window=14).mean().iloc[-1]
    high_volume = volume.iloc[-1] > volume_avg * 1.2

    # Log diagnostic info
    loggs.system_log.info(f"ADX: {adx.iloc[-1]}, ATR: {atr}, Volume: {volume.iloc[-1]}, "
                          f"Crossover Buy: {crossover_buy}, Crossover Sell: {crossover_sell}, "
                          f"RSI Long: {rsi_long}, RSI Short: {rsi_short}, "
                          f"Valid ATR: {valid_atr}, High Volume: {high_volume}")

    # Apply all conditions for trade signals
    if crossover_buy and strong_trend  and valid_atr and high_volume:
        return ['long', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]
    elif crossover_sell and strong_trend  and valid_atr and high_volume:
        return ['short', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]
    else:
        return ['Hold', curr_price, adx.iloc[-1], atr, rsi.iloc[-1], curr_long, curr_short, volume.iloc[-1]]