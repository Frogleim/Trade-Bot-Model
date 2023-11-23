import time
from datetime import datetime
import logging
import os
import sys
from binance.client import Client
import config
import files_manager

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
lookback_period = 15  # Number of periods to look back for range calculation
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
def range_trading_bot(symbol, interval, lookback_period, range_multiplier):
    global order_price
    while True:
        try:
            # Get historical data
            klines = get_historical_data(symbol, interval, lookback_period)
            klines_range = float(klines[-1][4])

            # Calculate trading range
            trading_range = calculate_range(klines)

            buy_threshold = klines_range - (float(trading_range) * float(range_multiplier))
            sell_threshold = klines_range + (float(trading_range) * float(range_multiplier))

            # Get current price
            current_price = float(client.get_ticker(symbol=symbol)['lastPrice'])

            logging.info(f'Current {config.trading_pair} price: {current_price} --- Buy Threshold: {buy_threshold}\n'
                         f'--- Sell threshold: {sell_threshold}')

            # Place buy order if the price is below the buy threshold
            if current_price < buy_threshold:
                logging.info(f"Placing buy order at {current_price}")
                entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                while True:
                    current_price_next = float(client.futures_ticker(symbol=symbol)['lastPrice'])
                    (profit) = float(current_price_next) - float(current_price)
                    logging.info(f'Current profit/loss: {round(profit, 1)} --- Current Price: {current_price_next}'
                                 f' --- Entry Price {current_price}')

                    # Save data for future dataset
                    files_manager.insert_data(current_price, current_price_next, profit, entry_time)

                    if profit >= 1.8:
                        # crypto_ticker.close_position(side='short', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Profit {profit}')
                        break
                    elif profit <= -0.569:
                        logging.info(f'Current profit/loss: {round(profit)}')
                        # crypto_ticker.close_position(side='short', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Loss {profit}')
                        break
            elif current_price > sell_threshold:
                logging.info(f"Placing sell order at {current_price}")

                entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                while True:
                    current_price_next = float(client.futures_ticker(symbol=symbol)['lastPrice'])
                    profit = float(current_price) - float(current_price_next)
                    logging.info(f'Current profit/loss: {round(profit, 1)} --- Current Price: {current_price_next}'
                                 f' --- Entry Price {current_price}')

                    # Save data for future dataset
                    files_manager.insert_data(current_price, current_price_next, profit, entry_time)

                    if profit >= 1.8:
                        # crypto_ticker.close_position(side='long', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Profit {profit}')
                        break

                    elif profit <= -0.569:
                        logging.info(f'Current profit/loss: {round(profit)}')
                        # crypto_ticker.close_position(side='long', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Loss {profit}')
                        break
            time.sleep(20)  # Wait for 1 minute before checking again

        except Exception as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    range_trading_bot(symbol, interval, lookback_period, range_multiplier)
