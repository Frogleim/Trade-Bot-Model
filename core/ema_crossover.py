from binance.client import Client
import pandas as pd
import ta
import time
import requests
import place_position
import numpy as np
import logging_settings
from coins_trade.miya import miya_trade


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


cred_data = get_credentials()
api_key = cred_data['api_key']
api_secret = cred_data['api_secret']
client = Client(api_key=api_key, api_secret=api_secret)
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
    long_ema = df['close'].ewm(span=8, adjust=False).mean()
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
        if adx.iloc[-1] > 20 or float(atr) > 100:
            return 'Buy', close_price
    elif crossover_sell:
        if adx.iloc[-1] > 20 or float(atr) > 100:
            return 'Sell', close_price
    else:
        return 'Hold', close_price


def start_trade(signal=None, close_price=None):
    signal, close_price = check_crossover()
    client.futures_change_leverage(leverage=125, symbol='BTCUSDT')
    try:
        if signal == 'Buy':
            logging_settings.system_log.warning(f'Buy position placed successfully: Entry Price: {close_price}')
            miya_trade.trade('BTCUSDT', signal=signal, entry_price=close_price, position_size=0.002, indicator='EMA')
            logging_settings.system_log.warning('Trade finished! Sleeping...')
            time.sleep(900)
        elif signal == 'Sell':
            logging_settings.system_log.warning(f'Sell position placed successfully. Entry Price: {close_price}')
            miya_trade.trade('BTCUSDT', signal=signal, entry_price=close_price, position_size=0.002, indicator='EMA')
            logging_settings.system_log.warning('Trade finished! Sleeping...')
            time.sleep(900)
        else:
            print('Hold, not crossover yet')
    except Exception as error:
        logging_settings.error_logs_logger.error(error)


if __name__ == '__main__':
    while True:
        try:
            start_trade()
            time.sleep(60)  # Sleep for 1 minute to avoid overloading
        except Exception as e:
            logging_settings.error_logs_logger.error(f"Error in trading loop: {e}")
            time.sleep(60)
