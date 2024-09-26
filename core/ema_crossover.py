from binance.client import Client
import pandas as pd
import ta
import time
import requests
import numpy as np


def write_system_state(e):
    with open("system_state.txt", 'w') as file:
        file.write(f'Not working\nReason {e}')


def get_credentials():
    print('Getting API KEYS from db')
    url = "http://77.37.51.134:8080/get_keys"
    headers = {
        "accept": "application / json"
    }
    response = requests.get(url=url, headers=headers, verify=False)
    return response.json()


# cred_data = get_credentials()
# api_key = cred_data['api_key']
# api_secret = cred_data['api_secret']
client = Client()
symbol = 'BTCUSDT'
interval = '5m'
lookback = 5
adx_period = 14


def calculate_ema():
    data = client.futures_klines(symbol=symbol, interval='5m')
    if not data or len(data) == 0:
        write_system_state("Empty data received from Binance")
        return None, None, None, None, None

    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    short_ema = df['close'].ewm(span=5, adjust=False).mean()
    long_ema = df['close'].ewm(span=13, adjust=False).mean()
    close_price = df['close'].iloc[-2]
    df['previous_close'] = df['close'].shift(1)
    df['high_low'] = df['high'] - df['low']
    df['high_prev_close'] = np.abs(df['high'] - df['previous_close'])
    df['low_prev_close'] = np.abs(df['low'] - df['previous_close'])
    df['true_range'] = df[['high_low', 'high_prev_close', 'low_prev_close']].max(axis=1)
    atr_period = 14
    df['ATR'] = df['true_range'].rolling(window=atr_period).mean()
    atr = df['ATR'].iloc[-1]
    adx = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)
    if adx is None or adx.iloc[-1] is None:
        write_system_state("ADX calculation failed")
        return None
    print(f'Long ema: {long_ema.iloc[-1]} Short ema: {short_ema.iloc[-1]} ATR: {df["ATR"].iloc[-2]}')
    return long_ema, short_ema, close_price, adx, atr


def check_crossover():
    short_ema, long_ema, close_price, adx, atr = calculate_ema()
    crossover_sell = (short_ema.iloc[-2] < long_ema.iloc[-2]) and (short_ema.iloc[-1] > long_ema.iloc[-1])
    crossover_buy = (short_ema.iloc[-2] > long_ema.iloc[-2]) and (short_ema.iloc[-1] < long_ema.iloc[-1])
    if crossover_buy:
        if adx.iloc[-1] > 20 and float(atr) > 65:
            return 'long', close_price, adx.iloc[-1], atr
    elif crossover_sell:
        if adx.iloc[-1] > 20 and float(atr) > 65:
            return 'short', close_price, adx.iloc[-1], atr
    else:
        return 'Hold', close_price, adx.iloc[-1], atr



def monitor_trade(close_price, atr, position_type='long'):
    if position_type == 'long':
        target_price = close_price + atr
        stop_loss = close_price - atr
    elif position_type == 'short':
        target_price = close_price - atr
        stop_loss = close_price + atr
    else:
        raise ValueError("position_type must be either 'long' or 'short'")

    while True:
        try:
            # Fetch the current price
            current_price = float(client.futures_ticker(symbol='BTCUSDT')['lastPrice'])
        except Exception as e:
            print(f"Error fetching price: {e}")
            time.sleep(1)  # Wait for a bit before retrying
            continue

        if position_type == 'long':
            # Check if target price is hit (Profit in long)
            if current_price >= target_price:
                return 'Profit', atr

            # Check if stop loss is hit (Loss in long)
            elif current_price < stop_loss:
                return 'Loss', -atr

        elif position_type == 'short':
            # Check if target price is hit (Profit in short)
            if current_price <= target_price:
                return 'Profit', atr

            # Check if stop loss is hit (Loss in short)
            elif current_price > stop_loss:
                return 'Loss', -atr

        # Optional: Sleep to avoid overwhelming the API with too many requests
        time.sleep(1)

# def start_trade(signal=None, close_price=None):
#
#     signal, close_price = check_crossover()
#     client.futures_change_leverage(leverage=125, symbol='BTCUSDT')
#     try:
#         if signal == 'Buy':
#             logging_settings.system_log.warning(f'Buy position placed successfully: Entry Price: {close_price}')
#             miya_trade.trade('BTCUSDT', signal=signal, entry_price=close_price, position_size=0.002, indicator='EMA')
#             logging_settings.system_log.warning('Trade finished! Sleeping...')
#             time.sleep(900)
#         elif signal == 'Sell':
#             logging_settings.system_log.warning(f'Sell position placed successfully. Entry Price: {close_price}')
#             miya_trade.trade('BTCUSDT', signal=signal, entry_price=close_price, position_size=0.002, indicator='EMA')
#             logging_settings.system_log.warning('Trade finished! Sleeping...')
#             time.sleep(900)
#         else:
#             print('Hold, not crossover yet')
#     except Exception as error:
#         logging_settings.error_logs_logger.error(error)


