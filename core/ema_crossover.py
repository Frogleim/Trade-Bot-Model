from binance.client import Client
import pandas as pd
import ta
import time
import requests
from position_handler import place_buy_order, place_sell_order
import place_position
import logging_settings
from coins_trade.miya import miya_trade

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
interval = '15m'
lookback = 5
adx_period = 14


def calculate_ema():
    data = client.futures_klines(symbol=symbol, interval='15m')
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

    adx = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)

    return long_ema, short_ema, close_price, adx


def check_crossover():
    short_ema, long_ema, close_price, adx = calculate_ema()
    crossover_sell = (short_ema.iloc[-2] < long_ema.iloc[-2]) and (short_ema.iloc[-1] > long_ema.iloc[-1])
    crossover_buy = (short_ema.iloc[-2] > long_ema.iloc[-2]) and (short_ema.iloc[-1] < long_ema.iloc[-1])
    print(crossover_sell)
    print(crossover_buy)
    if crossover_buy and adx.iloc[-1] > 20:
        return 'Buy', close_price
    elif crossover_sell and adx.iloc[-1] > 20:
        return 'Sell', close_price
    else:
        return 'Hold', close_price


def start_trade(signal=None, close_price=None):
    signal, close_price = check_crossover()
    client.futures_change_leverage(leverage=125, symbol='BTCUSDT')
    print(signal)
    if signal == 'Buy':
        logging_settings.system_log.warning(f'Buy position placed successfully: Entry Price: {close_price}')
        place_position.trade('BTCUSDT', signal=signal, entry_price=close_price, position_size=0.002)
        logging_settings.system_log.warning('Trade finished! Sleeping...')
        time.sleep(900)
    elif signal == 'Sell':
        logging_settings.system_log.warning(f'Sell position placed successfully. Entry Price: {close_price}')
        place_position.trade('BTCUSDT', signal=signal, entry_price=close_price, position_size=0.002)
        logging_settings.system_log.warning('Trade finished! Sleeping...')

        time.sleep(900)
    else:
        print('Hold, not crossover yet')


if __name__ == '__main__':
    while True:
        start_trade()
        time.sleep(10)

