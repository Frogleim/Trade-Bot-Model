from binance.client import Client
import logging
import os
import requests


def get_credentials():
    url = "http://77.37.51.134:8080/get_keys"
    headers = {
        "accept": "application / json"
    }
    response = requests.get(url=url, headers=headers, verify=False)
    return response.json()


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
keys_data = get_credentials()
API_KEY = keys_data['api_key']
API_SECRET = keys_data['api_secret']


def close_position(side, quantity):
    client = Client(api_key=API_KEY, api_secret=API_SECRET)
    if side == 'Buy':
        order = client.futures_create_order(
            symbol='BTCUSDT',
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantity,
        )
    else:
        order = client.futures_create_order(
            symbol='BTCUSDT',
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
    print(quantity)
    client = Client(api_key=API_KEY, api_secret=API_SECRET)
    order = client.futures_create_order(
        symbol=symbol,
        side='BUY',
        type=Client.ORDER_TYPE_MARKET,
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
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity,
    )
    print("Sell order placed successfully:")
    return order


if __name__ == "__main__":
    price = 0.553  # Example price for buying
    quantity = 10  # Example quantity
    symbol = 'MATICUSDT'
    stop_loss_price = 1.20  # Example stop loss price
    take_profit_price = 1.30  # Example take profit price

    place_buy_order(symbol=symbol, price=price, quantity=quantity)
