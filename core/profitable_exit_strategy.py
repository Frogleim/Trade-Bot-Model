from binance.client import Client
import pnl_calculator
import crypto_ticker
import files_manager
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
    global current_checkpoint
    if btc_price_change:
        profit_checkpoint_list.clear()
        current_checkpoint = None
        logging.info(f'Profit checkpoint list: {profit_checkpoint_list} --- Current checkpoint: {current_checkpoint}')
        crypto_ticker.place_buy_order(price=opened_price, quantity=config.position_size, symbol=config.trading_pair)
        body = f'Buying {config.trading_pair} for price {round(float(opened_price), 1)}'
        logging.info(body)
        while True:
            res = pnl_long(opened_price=opened_price, signal=signal_price)
            if res == 'Profit':
                crypto_ticker.close_position(side='short', quantity=config.position_size)
                pnl_calculator.position_size()
                logging.info('Position closed')
                break

    elif not btc_price_change:
        profit_checkpoint_list.clear()
        current_checkpoint = None
        logging.info(f'Profit checkpoint list: {profit_checkpoint_list} --- Current checkpoint: {current_checkpoint}')
        crypto_ticker.place_sell_order(price=opened_price, quantity=config.position_size, symbol=config.trading_pair)
        body = f'Selling {config.trading_pair} for price {round(float(opened_price), 1)}'
        logging.info(body)
        while True:
            res = pnl_short(opened_price=opened_price, signal=signal_price)
            if res == 'Profit':
                crypto_ticker.close_position(side='long', quantity=config.position_size)
                pnl_calculator.position_size()
                logging.info('Position closed')
                break


def check_price_changes():
    global checking_price, recent_signal

    while True:
        crypto_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
        logging.info(f'Current {config.trading_pair} price: {crypto_current}')
        checking_price = crypto_current
        time.sleep(config.ticker_timeout)
        next_crypto_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
        logging.info(f'New {config.trading_pair} price: {next_crypto_current}')
        signal_difference = float(next_crypto_current) - float(checking_price)
        logging.info(f'Difference: {round(signal_difference, 2)}')
        if signal_difference > config.signal_price and pnl_calculator.get_last_two_candles_direction(
                config.trading_pair) == 'Up':
            logging.info(pnl_calculator.get_last_two_candles_direction(
                config.trading_pair))
            message = (f"{config.trading_pair} goes up for more than {config.signal_price}$\n"
                       f" Buying {config.trading_pair} for {round(float(next_crypto_current), 1)}$")
            logging.info(message)
            return True, next_crypto_current, signal_difference
        elif signal_difference < -config.signal_price and pnl_calculator.get_last_two_candles_direction(
                config.trading_pair) == 'Down':
            logging.info(pnl_calculator.get_last_two_candles_direction(
                config.trading_pair))
            message = (f"{config.trading_pair} goes down for more than {config.signal_price}$\n"
                       f" Selling {config.trading_pair} for {round(float(next_crypto_current), 1)}$")
            logging.info(message)
            return False, next_crypto_current, signal_difference
        else:
            continue


def pnl_long(opened_price=None, current_price=2090, signal=None):
    global current_profit, current_checkpoint, profit_checkpoint_list, LOSS
    btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    current_profit = float(btc_current) - float(opened_price)
    logging.info(f'Entry Price: {opened_price} --- Current Price: {btc_current} --- Current Profit: {current_profit}')
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= current_profit < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:  # Check if it's a new checkpoint
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)

    logging.warning(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        if current_checkpoint < profit_checkpoint_list[-2] or current_checkpoint == config.checkpoint_list[-1]:
            body = f'Position closed!.\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            files_manager.insert_data(opened_price, btc_current, current_profit, signal)
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'


def pnl_short(opened_price=None, signal=None):
    global current_profit, current_checkpoint, profit_checkpoint_list, LOSS
    btc_current = client.futures_ticker(symbol=config.trading_pair)['lastPrice']
    current_profit = float(opened_price) - float(btc_current)
    logging.info(f'Entry Price: {opened_price} --- Current Price: {btc_current} --- Current Profit: {current_profit}')
    for i in range(len(config.checkpoint_list) - 1):
        if config.checkpoint_list[i] <= current_profit < config.checkpoint_list[i + 1]:
            if current_checkpoint != config.checkpoint_list[i]:
                current_checkpoint = config.checkpoint_list[i]
                profit_checkpoint_list.append(current_checkpoint)
                message = f'Current profit is: {current_profit}\nCurrent checkpoint is: {current_checkpoint}'
                logging.info(message)

    logging.warning(f'Current checkpoint: --> {current_checkpoint}')
    if len(profit_checkpoint_list) >= 2 and profit_checkpoint_list[-2] is not None and current_checkpoint is not None:
        if current_checkpoint < profit_checkpoint_list[-2] or current_checkpoint == config.checkpoint_list[-1]:
            body = f'Position closed!\nPosition data\nSymbol: {config.trading_pair}\nEntry Price: {round(float(opened_price), 1)}\n' \
                   f'Close Price: {round(float(btc_current), 1)}\nProfit: {round(current_profit, 1)}'
            logging.info(body)
            files_manager.insert_data(opened_price, btc_current, current_profit, signal)
            logging.info('Saving data')
            logging.info(f'Profit checkpoint list: {profit_checkpoint_list}')
            return 'Profit'


if __name__ == '__main__':
    while True:
        trade()
        time.sleep(config.TRADE_INTERVAL)
