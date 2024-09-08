import logging
import os
import sys
from collections import Counter
from binance.client import Client
from . import fetch_sma, api_connect

miya_api = api_connect.API()
keys_data = miya_api.get_binance_keys()
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
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "coins_trade")
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Set the desired log level for the console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)


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
        sma = fetch_sma.get_ema()
        if float(current_profit) <= float(sma):
            print('CLosing with lose')
            return 'Loss'
    else:
        if float(current_profit) <= -float(indicator_settings[0]['decimal_value']):
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
        current_price = client.futures_ticker(symbol=indicator_settings[0]['symbol'])['lastPrice']
    except Exception as e:
        current_price = client.futures_ticker(symbol=indicator_settings[0]['symbol'])['lastPrice']
    current_profit = float(opened_price) - float(current_price)
    for i in range(len(indicator_settings[0]['ratios']) - 1):
        if indicator_settings[0]['ratios'][i] <= current_profit < indicator_settings[0]['ratios'][i + 1]:
            if current_checkpoint != indicator_settings[0]['ratios'][i]:
                current_checkpoint = indicator_settings[0]['ratios'][i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
    if indicator == 'EMA':
        sma = fetch_sma.get_ema()
        if float(current_price) >= float(sma):
            print('CLosing with lose')
            return 'Loss'
    else:
        if float(current_profit) <= -float(indicator_settings[0]['decimal_value']):
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



if __name__ == '__main__':
    indicator_settings = miya_api.get_settings()
    print(indicator_settings)
    print(indicator_settings[0]['ratios'])
    print(indicator_settings[1])
    pnl_long(54600, 'EMA')