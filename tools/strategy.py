from .socket_binance import fetch_btcusdt_klines, get_last_price
from binance.client import Client
import requests
import time
from . import loggs
import ta
from dotenv import load_dotenv
import os

loaded = load_dotenv(dotenv_path='./tools/.env')
print(loaded)

client = Client()
symbol = os.getenv('SYMBOL')
interval = os.getenv('INTERVAL')
print(symbol, interval)
lookback = 5
adx_period = os.getenv('ADX_PERIOD')


def calculate_ema():
    """Calculating indicators including volume"""
    df = fetch_btcusdt_klines(symbol, interval)
    if df.empty:
        print("No data fetched.")
        return None, None, None, None, None, None

    # Calculate EMAs
    short_ema = df['close'].ewm(span=int(os.getenv('SHORT_EMA')), adjust=False).mean()
    long_ema = df['close'].ewm(span=int(os.getenv('LONG_EMA')), adjust=False).mean()

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
    df['volume'] = df['volume']  # Include volume from the fetched data

    loggs.system_log.info(
        f'Long EMA: {long_ema.iloc[-1]} Short EMA: {short_ema.iloc[-1]} ATR: {df["ATR"].iloc[-2]} ADX: {adx.iloc[-1]}'
        f' RSI: {rsi.iloc[-1]} RSI SMA: {rsi_sma.iloc[-1]} Volume: {df["volume"].iloc[-1]}')

    return long_ema, short_ema, close_price_series, adx, atr, rsi, df['volume']


def check_crossover():
    """Check for signal with improved strategy considering price movement and volume"""
    long_ema, short_ema, close_price_series, adx, atr, rsi, volume = calculate_ema()
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

    # Crossover conditions
    crossover_buy = (short_ema.iloc[-2] < long_ema.iloc[-2]) and (short_ema.iloc[-1] > long_ema.iloc[-1])
    crossover_sell = (short_ema.iloc[-2] > long_ema.iloc[-2]) and (short_ema.iloc[-1] < long_ema.iloc[-1])

    # Additional Indicator conditions
    additional_indicator_long = (adx.iloc[-1] > 20) and (rsi.iloc[-1] > 50)
    additional_indicator_short = (adx.iloc[-1] > 20) and (rsi.iloc[-1] < 50)

    # Volume analysis: Look for high volume for confirmation
    volume_threshold = 1000  # You can adjust this threshold based on your data
    high_volume = int(volume.iloc[-1]) > volume_threshold  # Check if the volume is above the threshold

    # Log diagnostic info
    loggs.system_log.info(f"ADX: {adx.iloc[-1]}, ATR: {atr}, Volume: {volume.iloc[-1]}, "
                          f"Crossover Buy: {crossover_buy}, Crossover Sell: {crossover_sell}, "
                          f"Other Buy: {additional_indicator_long}, Other Sell: {additional_indicator_short}, "
                          f"High Volume: {high_volume}")

    # Apply all conditions for trade signals
    if crossover_buy and additional_indicator_long and high_volume:
        return ['long', close_price_series.iloc[-1], adx.iloc[-1], atr, rsi.iloc[-1], long_ema.iloc[-1],
                short_ema.iloc[-1], high_volume]
    elif crossover_sell and additional_indicator_short and high_volume:
        return ['short', close_price_series.iloc[-1], adx.iloc[-1], atr, rsi.iloc[-1], long_ema.iloc[-1],
                short_ema.iloc[-1], high_volume]
    else:
        return ['Hold', close_price_series.iloc[-1], adx.iloc[-1], atr, rsi.iloc[-1], long_ema.iloc[-1],
                short_ema.iloc[-1], high_volume]

def long_trade(entry_price, atr):
    """Monitoring long trade"""
    loggs.system_log.warning(f'Buy position placed successfully: Entry Price: {entry_price}')

    if atr >= float(os.environ.get('ATR')):
        target_price = entry_price + atr
        stop_loss = entry_price - (atr / 2)
    else:
        target_price = entry_price + float(os.environ.get('ATR'))
        stop_loss = entry_price - (atr / 2 )
    while True:
        try:
            current_price = get_last_price()
        except Exception as e:
            print(f"Error fetching price: {e}")
            time.sleep(1)
            continue
        loggs.system_log.info(f'Entry Price: {entry_price} Target price: {target_price}, '
                              f'Current price: {current_price} Stop loss: {stop_loss}')
        if current_price >= target_price:
            return 'Profit', atr, target_price
        elif current_price <= stop_loss:
            return 'Loss', -atr, stop_loss
        time.sleep(1)

def short_trade(entry_price, atr):
    """Monitoring short trade"""

    loggs.system_log.warning(f'Sell position placed successfully: Entry Price: {entry_price}')
    if atr >= float(os.environ.get('ATR')):
        target_price = entry_price - float(os.environ.get('ATR'))
        stop_loss = entry_price + (atr / 2)
    else:
        target_price = entry_price - float(os.environ.get('ATR'))
        stop_loss = entry_price + (atr / 2)
    while True:
        try:
            current_price = get_last_price()
        except Exception as e:
            print(f"Error fetching price: {e}")
            time.sleep(1)
            continue
        loggs.system_log.info(f'Entry Price: {entry_price} Target price: {target_price}, '
                              f'Current price: {current_price} Stop loss: {stop_loss}')
        if current_price <= target_price:
            return 'Profit', atr, target_price
        elif current_price > stop_loss:
            return 'Loss', -atr, stop_loss
        time.sleep(1)




#
# if __name__ == '__main__':
#     while True:
#         check_crossover()