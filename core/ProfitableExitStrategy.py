from binance.client import Client
import pnl_calculator
import files_manager
import datetime
import logging
import config
import time
import sys
import os

current_profit = 0
position_mode = None
profit_checkpoint_list = []
recent_signal = []
current_checkpoint = None
THRESHOLD_FOR_CLOSING = -30
LOSS = False
checking_price = None
api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
client = Client(api_key, api_secret)
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "Trade-Bot")
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
        # crypto_ticker.place_buy_order(price=opened_price, quantity=config.position_size, symbol=config.trading_pair)
        open_time = time.time()
        dt_object = datetime.datetime.fromtimestamp(open_time)
        fixed_open_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        body = f'Buying {config.trading_pair} for price {round(float(opened_price), 1)}'
        logging.info(body)
        while True:
            # res = fix_price_pnl(entry_price=opened_price, signal=signal_price, open_time=fixed_open_time)
            res = pnl_long(opened_price=opened_price, signal=signal_price)
            if res == 'Profit':
                # crypto_ticker.close_position(side='short', quantity=config.position_size)
                logging.info('Position closed')
                pnl_calculator.position_size()
                break
            elif res == 'Loss':
                # crypto_ticker.close_position(side='short', quantity=config.position_size)
                logging.info('Position closed')
                break
    else:
        # crypto_ticker.place_sell_order(price=opened_price, quantity=config.position_size, symbol=config.trading_pair)
        open_time = time.time()
        dt_object = datetime.datetime.fromtimestamp(open_time)
        fixed_open_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
        body = f'Selling {config.trading_pair} for price {round(float(opened_price), 1)}'
        logging.info(body)
        while True:
            res = pnl_short(opened_price=opened_price, signal=signal_price)
            # res = fix_price_pnl_short(entry_price=opened_price, signal=signal_price, open_time=fixed_open_time)
            if res == 'Profit':
                # crypto_ticker.close_position(side='long', quantity=config.position_size)
                pnl_calculator.position_size()
                logging.info('Position closed')
                break
            elif res == 'Loss':
                # crypto_ticker.close_position(side='long', quantity=config.position_size)
                logging.info('Position closed')
                break


def check_price_changes():
    global checking_price, recent_signal

    while True:
        btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
        logging.info(f'Current {config.trading_pair} price: {btc_current}')
        checking_price = btc_current
        time.sleep(config.ticker_timeout)
        next_btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
        logging.info(f'New {config.trading_pair} price: {next_btc_current}')
        signal_difference = float(next_btc_current) - float(checking_price)
        logging.info(f'Difference: {signal_difference}')
        if len(recent_signal) > 0 and recent_signal[-2:] == 'Up':
            if signal_difference > config.signal_price:
                message = (f"{config.trading_pair} goes up for more than {config.signal_price}$\n"
                           f" Buying {config.trading_pair} for {round(float(next_btc_current), 1)}$")
                logging.info(message)
                recent_signal.append('Up')
                return True, next_btc_current, signal_difference
        elif len(recent_signal) > 0 and recent_signal[-2:] == 'Down':
            if signal_difference < -config.signal_price:
                message = (f"{config.trading_pair} goes down for more than {config.signal_price}$\n"
                           f" Selling {config.trading_pair} for {round(float(next_btc_current), 1)}$")
                logging.info(message)
                recent_signal.append('Down')
                return False, next_btc_current, signal_difference
        elif signal_difference > config.signal_price and pnl_calculator.get_last_two_candles_direction(config.trading_pair):
            message = (f"{config.trading_pair} goes up for more than {config.signal_price}$\n"
                       f" Buying {config.trading_pair} for {round(float(next_btc_current), 1)}$")
            logging.info(message)
            recent_signal.append('Up')
            return True, next_btc_current, signal_difference
        elif signal_difference < -config.signal_price and not pnl_calculator.get_last_two_candles_direction(config.trading_pair):
            message = (f"{config.trading_pair} goes down for more than {config.signal_price}$\n"
                       f" Selling {config.trading_pair} for {round(float(next_btc_current), 1)}$")
            logging.info(message)
            recent_signal.append('Down')
            return False, next_btc_current, signal_difference
        else:
            continue


def pnl_long(opened_price=None, current_price=2090, signal=None):
    global current_profit, current_checkpoint, profit_checkpoint_list, LOSS
    btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
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
            print(current_profit)
            body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            files_manager.insert_data(opened_price, btc_current, current_profit, signal)
            profit_checkpoint_list.clear()  # Reset the checkpoint list
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'
    elif LOSS:
        body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
               f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
        logging.info(body)
        files_manager.insert_data(opened_price, btc_current, current_profit, signal)
        profit_checkpoint_list.clear()  # Reset the checkpoint list
        logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
        return 'Loss'


def pnl_short(opened_price=None, signal=None):
    global current_profit, current_checkpoint, profit_checkpoint_list, LOSS
    btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
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
            body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            files_manager.insert_data(opened_price, btc_current, current_profit, signal)
            logging.info('Saving data')
            profit_checkpoint_list.clear()  # Reset the checkpoint list
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'

    elif LOSS:
        body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
               f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
        logging.info(body)
        files_manager.insert_data(opened_price, btc_current, current_profit, signal)
        logging.info('Saving data')
        profit_checkpoint_list.clear()  # Reset the checkpoint list
        logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
        return 'Loss'


if __name__ == '__main__':
    while True:
        trade()
        time.sleep(10)
