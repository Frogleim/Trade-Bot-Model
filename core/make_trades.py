import datetime
import time
from . import bitcoin_ticker, config, files_manager, pnl_calculator
# from . import logs_handler
# import bitcoin_ticker
import logging

import random
# import config
import os
import sys

current_profit = 0
position_mode = None
profit_checkpoint_list = []
current_checkpoint = None
THRESHOLD_FOR_CLOSING = -30
LOSS = False
checking_price = None

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "binance_bot")
logging.basicConfig(filename=f'{files_dir}/logs/binance_logs.log',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Set the desired log level for the console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)


def trade():
    btc_price_change, opened_price, signal_price = check_price_changes()
    if btc_price_change:
        # bitcoin_ticker.create_order(side='long')
        open_time = time.time()
        dt_object = datetime.datetime.fromtimestamp(open_time)
        fixed_open_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        body = f'Buying ETHUSDT for price {round(float(opened_price), 1)}'
        logging.info(body)
        while True:
            res = fix_price_pnl(entry_price=opened_price, signal=signal_price, open_time=fixed_open_time)
            # res = pnl_long(opened_price=opened_price, signal=signal_price)
            if res == 'Profit':
                # bitcoin_ticker.close_position(side='short', quantity=config.position_size)
                logging.info('Position closed')
                pnl_calculator.position_size()
                break
            elif res == 'Loss':
                # bitcoin_ticker.close_position(side='short', quantity=config.position_size)
                logging.info('Position closed')
                break
            time.sleep(random.uniform(0.6587, 1.11))
    else:
        # bitcoin_ticker.create_order(side='short')
        open_time = time.time()
        dt_object = datetime.datetime.fromtimestamp(open_time)
        fixed_open_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        body = f'Selling ETHUSDT for price {round(float(opened_price), 1)}'
        logging.info(body)
        while True:
            # res = pnl_short(opened_price=opened_price, signal=signal_price)
            res = fix_price_pnl_short(entry_price=opened_price, signal=signal_price, open_time=fixed_open_time)
            if res == 'Profit':
                # bitcoin_ticker.close_position(side='long', quantity=config.position_size)
                pnl_calculator.position_size()
                logging.info('Position closed')
                break
            elif res == 'Loss':
                # bitcoin_ticker.close_position(side='long', quantity=config.position_size)
                logging.info('Position closed')
                break
            time.sleep(random.uniform(0.6587, 1.11))


def check_price_changes():
    global checking_price

    while True:
        btc_current_class = bitcoin_ticker.LivePrice()
        btc_current = btc_current_class.get_live_price()
        print(btc_current)
        checking_price = btc_current
        time.sleep(config.ticker_timeout)
        next_btc_current_class = bitcoin_ticker.LivePrice()
        next_btc_current = next_btc_current_class.get_live_price()
        signal_difference = float(next_btc_current) - float(checking_price)
        if signal_difference > 30:
            message = f"ETHUSDT goes up for more than 1$\n Buying ETHUSDT for {round(float(next_btc_current), 1)}$"
            logging.info(message)
            return True, next_btc_current, signal_difference
        elif signal_difference < -30:
            message = f"ETHUSDT goes up for more than 1$\n Buying ETHUSDT for {round(float(next_btc_current), 1)}$"
            logging.info(message)

            return False, next_btc_current, signal_difference
        else:
            message = f"ETHUSDT price doesnt changed enough! Current price: {round(float(next_btc_current), 1)}"
            logging.info(message)

            continue


def fix_price_pnl(entry_price, signal, open_time):
    global current_profit, current_checkpoint, profit_checkpoint_list, LOSS
    btc_current_class = bitcoin_ticker.LivePrice()
    btc_current = btc_current_class.get_live_price()
    current_profit = float(btc_current) - float(entry_price)
    msg = f'Entry Price: {entry_price} --- Current Price: {btc_current} --- Current Profit: {current_profit}'
    logging.info(msg)
    if current_profit >= 40:
        close_time = time.time()
        dt_object = datetime.datetime.fromtimestamp(close_time)
        fixed_close_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        files_manager.insert_data(entry_price, btc_current, current_profit, signal, open_time, fixed_close_time)
        return 'Profit'
    elif current_profit <= -15:
        close_time = time.time()
        dt_object = datetime.datetime.fromtimestamp(close_time)
        fixed_close_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        files_manager.insert_data(entry_price, btc_current, current_profit, signal, open_time, fixed_close_time)
        return 'Loss'


def fix_price_pnl_short(entry_price, signal, open_time):
    global current_profit, current_checkpoint, profit_checkpoint_list, LOSS
    btc_current_class = bitcoin_ticker.LivePrice()
    btc_current = btc_current_class.get_live_price()
    current_profit = float(entry_price) - float(btc_current)
    msg = f'Entry Price: {entry_price} --- Current Price: {btc_current} --- Current Profit: {current_profit}'
    logging.info(msg)
    if current_profit >= 40:
        close_time = time.time()
        dt_object = datetime.datetime.fromtimestamp(close_time)
        fixed_close_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        files_manager.insert_data(entry_price, btc_current, current_profit, signal, open_time, fixed_close_time)

        return 'Profit'
    elif current_profit <= -15:
        close_time = time.time()
        dt_object = datetime.datetime.fromtimestamp(close_time)
        fixed_close_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        files_manager.insert_data(entry_price, btc_current, current_profit, signal, open_time, fixed_close_time)

        return 'Loss'


def pnl_long(opened_price=None, current_price=2090):
    global current_profit, current_checkpoint, profit_checkpoint_list, LOSS
    btc_current_class = bitcoin_ticker.LivePrice()
    btc_current = btc_current_class.get_live_price()
    trading_pair = 'ETHUSDT'
    current_profit = float(btc_current) - float(opened_price)
    print(f'Entry Price: {opened_price} --- Current Price: {btc_current} --- Current Profit: {current_profit}')
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= current_profit < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:  # Check if it's a new checkpoint
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
        elif current_profit <= -5:  # Stop loss on -9.52%
            LOSS = True
            logging.info('Losing money')
    print(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        if current_checkpoint < profit_checkpoint_list[-2] or current_checkpoint == config.checkpoint_list[-1]:
            print('Position closed!')
            profit_checkpoint_list = []
            print(current_profit)
            body = f'Position closed!\nPosition data\nSymbol: {trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            return 'Profit'
    elif LOSS:
        body = f'Position closed!\nPosition data\nSymbol: {trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
               f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
        logging.info(body)
        return 'Loss'


def pnl_short(opened_price=None, signal=None):
    global current_profit, current_checkpoint, profit_checkpoint_list, LOSS
    btc_current_class = bitcoin_ticker.LivePrice()
    btc_current = btc_current_class.get_live_price()
    trading_pair = 'ETHUSDT'
    current_profit = float(opened_price) - float(btc_current)
    print(f'Entry Price: {opened_price} --- Current Price: {btc_current} --- Current Profit: {current_profit}')
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= current_profit < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)
        elif current_profit <= -5:  # Stop loss on -9.52%
            LOSS = True
            logging.warning('Losing money')

    print(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        if current_checkpoint >= profit_checkpoint_list[-2] or current_checkpoint == config.checkpoint_list[-1]:
            profit_checkpoint_list = []
            body = f'Position closed!\nPosition data\nSymbol: {trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            files_manager.insert_data(opened_price, btc_current, current_profit, signal)
            logging.info('Saving data')

            return 'Profit'
    elif LOSS:
        body = f'Position closed!\nPosition data\nSymbol: {trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
               f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
        logging.info(body)
        files_manager.insert_data(opened_price, btc_current, current_profit, signal)
        logging.info('Saving data')
        return 'Loss'


if __name__ == '__main__':
    while True:
        trade()
        time.sleep(10)
