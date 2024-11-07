from binance.client import Client
import logging
import os
from dotenv import load_dotenv


load_dotenv(dotenv_path='.env')

previous_price = None
alert_status = False
return_response = None
price_threshold = 15
price_difference = 0.0

API_KEY=os.getenv("API_KEY")
API_SECRET=os.getenv("API_SECRET")


def close_position(symbol):
    position_size = None
    client = Client(api_key=API_KEY, api_secret=API_SECRET)

    position_info = client.futures_position_information(symbol=symbol)
    print(position_info)
    for position in position_info:
        if position['symbol'] == symbol:
            position_size = float(position['positionAmt'])
            print(position_size)

            break

    if position_size > 0:  # Long position, so sell to close
        order = client.futures_create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=position_size
        )
        print("Closed Long Position:", order)
    elif position_size < 0:  # Short position, so buy to close
        order = client.futures_create_order(
            symbol=symbol,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=abs(position_size)
        )
        print("Closed Short Position:", order)
    else:
        print("No open position to close.")


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


def place_buy_order(quantity, symbol):
    client = Client(api_key=API_KEY, api_secret=API_SECRET)
    order = client.futures_create_order(
        symbol=symbol,
        side=Client.SIDE_BUY,
        type=Client.ORDER_TYPE_MARKET,
        quantity=quantity,
    )

    print("Buy order placed successfully:")
    print(order)
    return order


def place_sell_order(quantity, symbol):

    client = Client(api_key=API_KEY, api_secret=API_SECRET)

    order = client.futures_create_order(
        symbol=symbol,
        side=Client.SIDE_SELL,
        type='MARKET',
        quantity=quantity,
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
    symbol = 'BTCUSDT'
    place_sell_order(symbol='BTCUSDT', quantity=0.002)
    close_position(symbol)
