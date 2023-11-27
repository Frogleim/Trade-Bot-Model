import time
import config
# from . import config
import os
from binance.client import Client

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
files_dir = os.path.join(parent_dir, "core")
print(files_dir)


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
    percentage_increase = 0.20
    new_value = original_value + (original_value * percentage_increase)
    print("Original Value:", original_value)
    print("Percentage Increase:", percentage_increase)
    print("New Value:", new_value)
    time.sleep(1)
    config.position_size = new_value
    with open(f'{files_dir}/config.py', 'r') as config_file:
        config_data = config_file.read()
    config_data = config_data.replace(f"position_size = {original_value}", f"position_size = {new_value}")
    with open(f'{files_dir}/config.py', 'w') as config_file:
        config_file.write(config_data)
    return original_value


api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')
# Replace 'YOUR_API_KEY' and 'YOUR_API_SECRET' with your Binance API key and secret
client = Client(api_key, api_secret)


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


if __name__ == '__main__':
    starting_number = 0.21  # 0.21$
    common_ratio = 1.10  # 20% increase
    num_terms = 64
    result = geometric_progression(starting_number, common_ratio, num_terms)
    print(result)
    wallet = [new_value + 4.32 for new_value in result]
    print(wallet)

    # symbol = 'ETHUSDT'
    # direction = get_last_two_candles_direction(symbol)
    # print(f'The direction of the last two candles on {symbol}: {direction}')
    #
