from binance.client import Client
import time
import config
import os
import logging
import sys

# Binance API keys
api_key = 'your_api_key'
api_secret = 'your_api_secret'

# Initialize Binance client
client = Client(config.API_KEY, config.API_SECRET, testnet=True)

# Define trading parameters
symbol = 'ETHUSDT'  # Replace with your desired trading pair
quantity = 0.001  # Replace with your desired trading quantity
profit_target_percent = 0.2  # Target profit percentage
stop_loss_percent = 0.1  # Stop-loss percentage
candlestick_interval = '1m'  # 1-minute candles
base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "Trade-Bot")
logging.basicConfig(filename=f'{files_dir}/logs/scalping_logs.log',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Set the desired log level for the console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)


# Function to get current price
def get_current_price():
    ticker = client.get_ticker(symbol=symbol)
    return float(ticker['lastPrice'])


# Function to place a market buy order
def place_buy_order(quantity):
    order = client.create_test_order(
        symbol=symbol,
        side='BUY',
        type='MARKET',
        quantity=quantity,
        test=True
    )
    return order


# Function to place a market sell order
def place_sell_order(quantity):
    order = client.create_test_order(
        symbol=symbol,
        side='SELL',
        type='MARKET',
        quantity=quantity,
        test=True
    )
    return order


# Main scalping function
def scalping_strategy():
    while True:
        try:
            # Get current price
            current_price = get_current_price()

            # Place buy order if the price is below the previous buy price
            buy_order_price = current_price * (1 - stop_loss_percent)
            logging.info(f'Current Price: {current_price} --- Buy Order Price: {buy_order_price}')
            if current_price < buy_order_price:
                order = place_buy_order(quantity)
                logging.info(f"Placed BUY order at {current_price}")
                logging.info(f"Order details: {order}")
                time.sleep(2)  # Wait for order to be executed

                # Place sell order at a profit target
                sell_price = current_price * (1 + profit_target_percent)
                order = place_sell_order(quantity)
                logging.info(f"Placed SELL order at {sell_price}")
                logging.info(f"Order details: {order}")
                time.sleep(2)  # Wait for order to be executed

        except Exception as e:
            logging.error(f"An error occurred: {e}")

        time.sleep(5)  # Adjust the interval based on your strategy requirements


if __name__ == "__main__":
    scalping_strategy()
