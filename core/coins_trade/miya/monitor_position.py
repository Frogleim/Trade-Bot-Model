from binance.client import Client
from . import logging_settings, fetch_sma


client = Client()


def monitor_position_long(entry_price):
    take_profit = 80.0
    sma = fetch_sma.get_ema()

    try:
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']
    except Exception as e:
        logging_settings.error_logs_logger.error(e)
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']

    if float(current_price) + 80 > take_profit:
        return 'Profit'
    elif float(current_price) < sma:
        return 'Loss'


def monitor_position_short(entry_price):
    take_profit = 80.0
    sma = fetch_sma.get_ema()

    try:
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']
    except Exception as e:
        logging_settings.error_logs_logger.error(e)
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']

    if float(current_price) - take_profit < entry_price:
        return 'Profit'
    elif float(current_price) > sma:
        return 'Loss'

