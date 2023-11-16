import random
from binance.client import Client
from . import config
import logging
import os
import time


previous_price = None
alert_status = False
return_response = None
price_threshold = 15
price_difference = 0.0
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
files_dir = os.path.join(parent_dir, "logs")
logging.basicConfig(filename=f'{files_dir}/binance_logs.log',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class LivePrice:
    def __init__(self):
        try:
            self.client = Client(api_key=config.API_KEY, api_secret=config.API_SECRET)
        except Exception:
            print('Connection lost! Reconnecting...')
            self.client = Client(api_key=config.API_KEY, api_secret=config.API_SECRET)

        self.trading_pair = 'ETHUSDT'  # Replace with the trading pair you want to check
        self.btc_current_price = None

    def get_live_price(self):
        try:
            ticker = self.client.futures_ticker(symbol=self.trading_pair)
        except Exception:
            print('Connection lost! Reconnecting...')
            time.sleep(random.uniform(1.8, 2.63))
            ticker = self.client.futures_mark_price(symbol=self.trading_pair)
        try:
            self.btc_current_price = ticker['lastPrice']
        except KeyError as e:
            logging.error(e)
            self.btc_current_price = ticker['markPrice']
        return self.btc_current_price


def get_price_ticker():
    global previous_price, price_threshold, price_difference

    client = Client(config.API_KEY, config.API_SECRET)
    trading_pair = 'BTCUSDT'  # Replace with the trading pair you want to check
    try:
        ticker = client.futures_mark_price(symbol=trading_pair)
    except Exception:
        print('Connection lost! Reconnecting...')
        time.sleep(random.uniform(1.8, 2.63))
        ticker = client.futures_mark_price(symbol=trading_pair)

    btc_current_price = ticker['markPrice']
    print(f'Bitcoin Current price: {round(float(btc_current_price), 2)}')
    if previous_price is not None:
        price_difference = float(btc_current_price) - float(previous_price)
        if price_difference >= price_threshold:
            print(f'Price goes up! Buy some crypto!\n'
                  f'Price difference: {price_difference}')
            return_response = "Price goes up"
            alert_status = True
        elif price_difference < -price_threshold:
            print(f'Price goes down! Sell some crypto!\n'
                  f'Price difference: {price_difference}')
            return_response = "Price goes down"
            alert_status = True
        else:
            return_response = "Price is stable"
            alert_status = False

    previous_price = btc_current_price
    return price_difference, btc_current_price


def get_account_balance(client):
    account_info = client.futures_account()
    balance = float(account_info['totalWalletBalance'])
    return balance


def get_ask_price(client, symbol):
    order_book = client.get_order_book(symbol=symbol)
    ask_price = float(order_book['asks'][0][0])
    return ask_price


def create_order(side, percentage_of_balance=95):
    client = Client(config.API_KEY, config.API_SECRET)
    symbol = 'ETHUSDT'
    ticker = client.futures_mark_price(symbol=symbol)
    btc_current_price = ticker['markPrice']
    balance = get_account_balance(client)
    quantity = balance / float(btc_current_price)
    print(round(quantity, 1))
    if side == 'long':
        order = client.futures_create_order(
            symbol=symbol,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=0.01,
        )
        print(order)
        print("Order opened successfully")
        return order['orderId'], round(quantity, 1)
    elif side == 'short':
        order = client.futures_create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=0.01,
        )
        print(order)
        print("Order opened successfully")
        return order['orderId'], round(quantity, 1)


def close_position(side, quantity):
    client = Client(config.API_KEY, config.API_SECRET)
    if side == 'long':
        order = client.futures_create_order(
            symbol='ETHUSDT',
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,
        )
    else:
        order = client.futures_create_order(
            symbol='ETHUSDT',
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,
        )
    print(order)
    print("Position closed successfully")


# if __name__ == "__main__":
#     import time
#
#     start_time = time.time()
#     # client = Client(config.API_KEY, config.API_SECRET)
#
#     # btc_current_class = LivePrice()
#     # btc_current = btc_current_class.get_live_price()
#     close_position('long', 0.01)
#     end_time = time.time()
#     total_time = end_time - start_time
#     print(total_time)
