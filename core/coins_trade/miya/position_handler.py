from binance.client import Client
from . import config, api_connect
import logging
import os

previous_price = None
alert_status = False
return_response = None
price_threshold = 15
price_difference = 0.0
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
miya_api = api_connect.API()
keys_data = miya_api.get_binance_keys()
API_KEY = keys_data['api_key']
API_SECRET = keys_data['api_secret']
print(API_KEY)
print(API_SECRET)


def close_position(side, quantity):
    client = Client(api_key=API_KEY, api_secret=API_SECRET)
    if side == 'long':
        order = client.futures_create_order(
            symbol=config.trading_pair,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,
        )
    else:
        order = client.futures_create_order(
            symbol=config.trading_pair,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,

            quantity=quantity,
        )
    print(order)
    print("Position closed successfully")


def place_buy_order_with_stop_loss_take_profit(price, quantity, symbol, stop_loss_price, take_profit_price):
    client = Client(api_key=API_KEY, api_secret=API_SECRET)

    # Place the buy order
    buy_order = client.futures_create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type='LIMIT',
        timeInForce='GTC',  # Good 'til canceled
        quantity=quantity,
        price=price
    )

    print("Buy order placed successfully:")
    print(buy_order)

    # Place OCO (One Cancels the Other) order for stop loss and take profit
    take_profit_limit = client.futures_create_order(
        symbol=symbol,
        side='SELL',
        positionSide='LONG',
        type='TAKE_PROFIT_LIMIT',
        timeInForce='GTC',  # GTC (Good 'Til Canceled)
        quantity=0.001,
        price=take_profit_price,  # Specify the take profit price
        stopPrice=take_profit_price,  # Specify the trigger price
        closePosition=True
    )

    print("OCO order for stop loss and take profit placed successfully:")


def place_buy_order(price, quantity, symbol):
    client = Client(api_key=API_KEY, api_secret=API_SECRET)
    order = client.futures_create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        timeInForce='GTC',  # Good 'til canceled
        quantity=quantity,
    )

    print("Buy order placed successfully:")
    print(order)
    return order


def place_sell_order(price, quantity, symbol):

    client = Client(api_key=API_KEY, api_secret=API_SECRET)

    order = client.futures_create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type='LIMIT',
        timeInForce='GTC',  # Good 'til canceled
        quantity=quantity,
        price=price
    )

    print("Sell order placed successfully:")
    return order


def get_balance():
    client = Client(api_key=API_KEY, api_secret=API_SECRET)
    data = client.futures_account_balance()
    for assets in data:
        if assets['asset'] == 'USDT':
            print(assets)


if __name__ == "__main__":
    get_balance()
