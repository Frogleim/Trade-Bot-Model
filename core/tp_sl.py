import logging
from collections import Counter
from binance.client import Client
from ema_crossover import get_credentials
import api_connect
import pandas as pd


keys_data = get_credentials()
miya_api = api_connect.API()
API_KEY = keys_data['api_key']
API_SECRET = keys_data['api_secret']
current_profit = 0
profit_checkpoint_list = []
current_checkpoint = 0.00
try:
    client = Client(API_KEY, API_SECRET)
except Exception as e:
    print(e)
    client = Client(API_KEY, API_SECRET)
price_history = []


def fetch_sma():
    data = client.futures_klines(symbol='BTCUSDT', interval='5m')
    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    long_ema = df['close'].ewm(span=8, adjust=False).mean()
    return long_ema.iloc[-1]


def pnl_long(opened_price, indicator):
    indicator_settings = miya_api.get_settings()

    global current_profit, current_checkpoint, profit_checkpoint_list
    try:
        current_price = client.futures_ticker(symbol=indicator_settings[0]['symbol'])['lastPrice']
    except Exception as e:
        current_price = client.futures_ticker(symbol=indicator_settings[0]['symbol'])['lastPrice']

    current_profit = float(current_price) - float(opened_price)
    for i in range(len(indicator_settings[0]['ratios']) - 1):
        if indicator_settings[0]['ratios'][i] <= current_profit < indicator_settings[0]['ratios'][i + 1]:
            if current_checkpoint != indicator_settings[0]['ratios'][i]:  # Check if it's a new checkpoint
                current_checkpoint = indicator_settings[0]['ratios'][i] * 1.15
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
    if indicator == 'EMA':
        sma = fetch_sma()
        if float(current_profit) <= float(sma):
            print('CLosing with lose')
            return 'Loss'
    else:
        if float(current_profit) <= -float(indicator_settings[4]):
            print('CLosing with lose')
            return 'Loss'
    logging.warning(
        f'Current checkpoint: --> {current_checkpoint} --> {current_profit} --> Current Price {current_price}')

    if len(profit_checkpoint_list) >= 1 and current_checkpoint is not None:
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if (current_profit < profit_checkpoint_list[-1] or current_checkpoint >= indicator_settings[0]['ratios'][-1]
                and current_profit > 0):
            body = \
                f'Position closed!.\nPosition data\nSymbol: {indicator_settings[1]}\nEntry Price: {round(float(opened_price), 1)}\n' \
                f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')

            return 'Profit'


def pnl_short(opened_price, indicator):
    indicator_settings = miya_api.get_settings()

    global current_profit, current_checkpoint, profit_checkpoint_list
    try:
        current_price = client.futures_ticker(symbol=indicator_settings[1])['lastPrice']
    except Exception as e:
        current_price = client.futures_ticker(symbol=indicator_settings[1])['lastPrice']
    current_profit = float(opened_price) - float(current_price)
    for i in range(len(indicator_settings[0]['ratios']) - 1):
        if indicator_settings[0]['ratios'][i] <= current_profit < indicator_settings[0]['ratios'][i + 1]:
            if current_checkpoint != indicator_settings[0]['ratios'][i]:
                current_checkpoint = indicator_settings[0]['ratios'][i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
    if indicator == 'EMA':
        sma = fetch_sma()
        if float(current_price) >= float(sma):
            print('CLosing with lose')
            return 'Loss'
    else:
        if float(current_profit) <= -float(indicator_settings[4]):
            print('CLosing with lose')
            return 'Loss'
    logging.warning(
        f'Current checkpoint: --> {current_checkpoint} --> {current_profit} --> Current Price {current_price}')
    if len(profit_checkpoint_list) >= 1 and current_checkpoint is not None:
        logging.info('Checking for duplicates...')
        profit_checkpoint_list = list(Counter(profit_checkpoint_list).keys())
        logging.info(f'Checkpoint List is: {profit_checkpoint_list}')
        if (current_profit < profit_checkpoint_list[-1] or current_checkpoint >= indicator_settings[0]['ratios'][-1]
                and current_profit > 0):
            body = f'Position closed!\nPosition data\nSymbol: {indicator_settings[1]}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(current_price), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            logging.info('Saving data')
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')

            return 'Profit'
