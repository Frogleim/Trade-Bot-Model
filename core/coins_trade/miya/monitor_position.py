from binance.client import Client
import logging_settings, fetch_sma


client = Client()


def monitor_position_long(entry_price):
    take_profit = 80.0
    sma = fetch_sma.get_ema()

    try:
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']
    except Exception as e:
        logging_settings.error_logs_logger.error(e)
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']

    if entry_price + take_profit >= float(current_price):
        return 'Profit'
    elif current_price < sma:
        return 'Loss'


def monitor_position_short(entry_price):
    take_profit = 80.0
    sma = fetch_sma.get_ema()

    try:
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']
    except Exception as e:
        logging_settings.error_logs_logger.error(e)
        current_price = client.futures_ticker(symbol='BTCUSDT')['lastPrice']

    if entry_price - take_profit <= float(current_price):
        return 'Profit'
    elif current_price > sma:
        return 'Loss'

