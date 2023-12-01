import time
import config
import os
from binance.client import Client
from binance.helpers import round_step_size  # add at top

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
files_dir = os.path.join(parent_dir, "core")
print(files_dir)
client = Client(config.API_KEY, config.API_SECRET)


class BinanceFuturesPNLCalculator:
    def __init__(self, entry_price, exit_price, quantity, leverage):
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.quantity = quantity
        self.leverage = leverage

    def calculate_pnl(self):
        pnl = ((self.exit_price - self.entry_price) / self.entry_price) * self.quantity * self.leverage
        return pnl


def geometric_progression(starting_number, ratio, count):
    """
    Generate a geometric progression.

    Parameters:
    - starting_number: The first term of the geometric progression.
    - ratio: The common ratio.
    - count: The number of terms to generate.

    Returns:
    A list containing the terms of the geometric progression.
    """
    progression = [starting_number * (ratio ** i) for i in range(count)]
    return progression


def calculate_modified_difference(lst):
    modified_values = [(lst[i] - lst[i + 1]) * (1 - 0.005) for i in range(len(lst) - 1)]
    return modified_values


def position_size():
    original_value = config.position_size
    percentage_increase = 0.05
    new_value = original_value + (original_value * percentage_increase)
    print("Original Value:", original_value)
    print("Percentage Increase:", percentage_increase)
    print("New Value:", new_value)
    time.sleep(1)
    config.position_size = round(new_value, 3)
    with open(f'{files_dir}/config.py', 'r') as config_file:
        config_data = config_file.read()
    config_data = config_data.replace(f"position_size = {original_value}", f"position_size = {new_value}")
    with open(f'{files_dir}/config.py', 'w') as config_file:
        config_file.write(config_data)
    return original_value


def get_symbol_precision(symbol):
    exchange_info = client.get_exchange_info()

    for symbol_info in exchange_info['symbols']:
        if symbol_info['symbol'] == symbol:
            return int(symbol_info['baseAssetPrecision'])

    # If the symbol is not found, you may want to handle this case appropriately
    raise ValueError(f"Symbol {symbol} not found in exchange info")

# Example usage for ETHUSDT



def get_last_two_candles_direction(symbol, interval='5m'):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=5)
    close_prices = [float(kline[4]) for kline in klines[:-1]]
    if close_prices[-1] > close_prices[-2]:
        print(close_prices[-1])
        print(close_prices[-2])
        direction = True
    elif close_prices[-1] < close_prices[-2]:
        direction = False
    else:
        direction = 'No Change'

    return direction


def get_current_positions():
    # Replace YOUR_API_KEY and YOUR_API_SECRET with your Binance API key and secret
    client = Client(api_key='KH3zUXPCNXCI8mkVymna2cG3tkYm2daQtgPBsQpSdOwZlOcTQuqoQVvA9mSvpQfA',
                    api_secret='7TMJtn1N0B6cw875KgjD2jV1oxcLm6zcl5rPEt8uSJZeMmZs3JJrD1NxteVScPkb')

    client_test = Client(config.API_KEY, config.API_SECRET, testnet=True)
    price = 2059
    cost = float(str(price).split('.')[0] + "." + str(price).split('.')[1][0:5]) + (price * 0.3 / 100)

    # Get current open positions
    data = client.futures_exchange_info()  # request data
    info = data['symbols']  # pull list of symbols
    for x in range(len(info)):  # find length of list and run loop
        if info[x]['symbol'] == config.trading_pair:  # until we find our coin
            a = info[x]["filters"][0]['tickSize']  # break into filters pulling tick size
            cost = round_step_size(cost,
                                   float(a))  # convert tick size from string to float, insert in helper func with cost
            print(cost)  # run into order parameter as price=cost


if __name__ == '__main__':
    symbol_precision_ethusdt = get_symbol_precision('ETHUSDT')
    print(f"Symbol Precision for ETHUSDT: {symbol_precision_ethusdt}")
    starting_number = 300  # 0.21$
    common_ratio = 1.05  # 20% increase
    num_terms = 80  # 40 Trades is one day trade
    result = geometric_progression(starting_number, common_ratio, num_terms)
    print(result)
    wallet = [new_value + 90 for new_value in result]
    print(wallet)
