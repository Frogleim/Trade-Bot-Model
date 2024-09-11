from binance.client import Client
from . import logging_settings, fetch_sma, api_connect

miya_api = api_connect.API()
keys_data = miya_api.get_binance_keys()
API_KEY = keys_data['api_key']
API_SECRET = keys_data['api_secret']
client = Client(API_KEY, API_SECRET)


def monitor_position_long(entry_price):
    take_profit = 80.0
    sma = fetch_sma.get_ema()
    position_info = client.futures_position_information(symbol='BTCUSDT')
    target = entry_price + 100

    try:
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']
    except Exception as e:
        logging_settings.error_logs_logger.error(e)
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']
    profit_difference = float(current_price) - entry_price

    if profit_difference > 100:
        return 'Profit'
    elif float(current_price) < sma:
        return 'Loss'


def monitor_position_short(entry_price):
    take_profit = 80.0
    sma = fetch_sma.get_ema()
    target = entry_price - 100

    try:
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']
    except Exception as e:
        logging_settings.error_logs_logger.error(e)
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']
    profit_difference = float(current_price) - entry_price
    if profit_difference < -100:
        return 'Profit'
    elif float(current_price) > sma:
        return 'Loss'


if __name__ == '__main__':
    entry = 56426
    long_target = entry + 80
    short_target = entry - 80
    monitor_position_short(entry_price=entry)
