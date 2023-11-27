import time
import config
# from . import config
import os

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


if __name__ == '__main__':
    starting_number = 1000  # 0.21$
    common_ratio = 1.016  # 20% increase
    num_terms = 64
    result = geometric_progression(starting_number, common_ratio, num_terms)
    print(result)
#     import datetime
#     import time
#
#     # Replace timestamp with your specific timestamp
#     timestamp = time.time()
#
#     # Convert timestamp to a datetime object
#     dt_object = datetime.datetime.fromtimestamp(timestamp)
#
#     # Format the datetime object as a string in the desired format
#     formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
#
#     print(formatted_time)
