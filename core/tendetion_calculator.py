from binance.client import Client
import time
import config
import crypto_ticker
import files_manager
import logging
import os
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
grandparent_dir = os.path.dirname(parent_dir)
files_dir = os.path.join(grandparent_dir, "binance_bot")
logging.basicConfig(filename=f'{files_dir}/logs/binance_logs.log',
                    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)  # Set the desired log level for the console
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)

order_price = None
# Initialize Binance client
client = Client(config.API_KEY, config.API_SECRET)

# Define trading parameters
symbol = 'ETHUSDT'  # Replace with your desired trading pair
interval = '5m'  # 5-minute candles
lookback_period = 20  # Number of periods to look back for range calculation
range_multiplier = 0.01  # Range multiplier to set buy and sell thresholds


# Function to get historical klines data
def get_historical_data(symbol, interval, lookback_period):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=lookback_period)
    return klines


# Function to calculate trading range
def calculate_range(klines):
    closes = [float(kline[4]) for kline in klines]
    trading_range = max(closes) - min(closes)
    return trading_range


# Main trading function
# ... (your imports and API key initialization)

# Main trading function
def range_trading_bot(symbol, interval, lookback_period, range_multiplier):
    global order_price
    while True:
        try:
            # Get historical data
            klines = get_historical_data(symbol, interval, lookback_period)
            print("Klines:", klines)  # Add this line to inspect the klines data
            klines_range = float(klines[-1][4])

            # Calculate trading range
            trading_range = calculate_range(klines)

            # Set buy and sell thresholds
            buy_threshold = klines_range - (float(trading_range) * float(range_multiplier))
            sell_threshold = klines_range + (float(trading_range) * float(range_multiplier))

            # Get current price
            current_price = float(client.get_ticker(symbol=symbol)['lastPrice'])
            logging.info(f'Current {config.trading_pair} price: {current_price} --- Trading range: {trading_range}')

            # Place buy order if the price is below the buy threshold
            if current_price < buy_threshold:
                logging.info(f"Placing buy order at {current_price}")
                # crypto_ticker.place_buy_order(
                #     price=current_price,
                #     quantity=config.position_size,
                #     symbol=config.trading_pair
                # )
                order_price = current_price
                while True:
                    current_price_next = float(client.futures_ticker(symbol=symbol)['lastPrice'])
                    (profit) = float(current_price_next) - float(current_price)
                    logging.info(f'Current profit/loss: {round(profit)}')
                    if profit >= 2.5:
                        # crypto_ticker.close_position(side='short', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Profit {profit}')
                        files_manager.insert_data(current_price, current_price_next, profit)
                    elif profit <= -2.5:
                        logging.info(f'Current profit/loss: {round(profit)}')
                        # crypto_ticker.close_position(side='short', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Loss {profit}')
                        files_manager.insert_data(current_price, current_price_next, profit)
            elif current_price > sell_threshold:
                # crypto_ticker.place_sell_order(
                #     price=current_price,
                #     quantity=config.position_size,
                #     symbol=config.trading_pair
                # )
                logging.info(f"Placing sell order at {current_price}")
                while True:
                    current_price_next = float(client.get_ticker(symbol=symbol)['lastPrice'])
                    profit = float(current_price) - float(current_price_next)
                    logging.info(f'Current profit/loss: {round(profit)}')
                    if profit >= 2.5:
                        # crypto_ticker.close_position(side='long', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Profit {profit}')
                        files_manager.insert_data(current_price, current_price_next, profit)

                    elif profit <= -2.5:
                        logging.info(f'Current profit/loss: {round(profit)}')
                        # crypto_ticker.close_position(side='long', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Loss {profit}')
                        files_manager.insert_data(current_price, current_price_next, profit)

            time.sleep(60)  # Wait for 1 minute before checking again

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    range_trading_bot(symbol, interval, lookback_period, range_multiplier)
