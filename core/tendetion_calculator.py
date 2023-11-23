from binance.client import Client
import time
import config
import crypto_ticker
import files_manager
from sklearn.linear_model import LinearRegression
import numpy as np
from joblib import dump, load

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
model_filename = 'linear_regression_model.joblib'
if os.path.exists(model_filename):
    model = load(model_filename)
else:
    model = LinearRegression()

price_change_prediction = 0.0
order_price = None
# Initialize Binance client
client = Client(config.API_KEY, config.API_SECRET)

# Define trading parameters
symbol = 'ETHUSDT'  # Replace with your desired trading pair
interval = '5m'  # 5-minute candles
lookback_period = 20  # Number of periods to look back for range calculation
range_multiplier = 0.01  # Range multiplier to set buy and sell thresholds


# Function to get historical klines data
def train_model(X, y):
    # Fit the model with the new data
    model.fit(X, y)


def predict_price_change(X):
    # Reshape the input to a 2D array
    X_2d = np.array(X).reshape(1, -1) if len(X) == 1 else np.array(X).reshape(-1, 1)

    # Predict the price change based on the model
    return model.predict(X_2d)
def get_historical_data(symbol, interval, lookback_period):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=lookback_period)
    return klines


# Function to calculate trading range
def calculate_range(klines):
    closes = [float(kline[4]) for kline in klines]
    trading_range = max(closes) - min(closes)
    return trading_range

def is_model_fitted(model):
    return hasattr(model, 'coef_') and hasattr(model, 'intercept_')


# Main trading function
# ... (your imports and API key initialization)

# Main trading function
def range_trading_bot(symbol, interval, lookback_period, range_multiplier):
    global order_price
    X, y = [], []
    price_change_prediction = 0.0  # Move this inside the trading loop
    while True:
        # try:
            # Get historical data
            klines = get_historical_data(symbol, interval, lookback_period)
            klines_range = float(klines[-1][4])

            # Calculate trading range
            trading_range = calculate_range(klines)

            # Get current price
            current_price = float(client.futures_ticker(symbol=symbol)['lastPrice'])

            # Set buy and sell thresholds
            buy_threshold = klines_range - (float(trading_range) * float(range_multiplier))
            sell_threshold = current_price + (float(trading_range) * float(range_multiplier))
            logging.info(f'Current {config.trading_pair} price: {current_price} --- Buy Threshold: {buy_threshold}\n'
                         f'--- Sell threshold: {sell_threshold}')

            features = [[current_price, trading_range]]  # Wrap the features in a list

            # Check if the model is already fitted
            if is_model_fitted(model):
                price_change_prediction = predict_price_change(features)

                # Place buy order if the price change is positive
                if price_change_prediction > 0:
                    logging.info(f"Placing buy order at {current_price}")
                    # Your buy order logic here
                    while True:
                        current_price_next = float(client.futures_ticker(symbol=symbol)['lastPrice'])
                        profit = float(current_price_next) - float(current_price)
                        logging.info(f'Current profit/loss: {round(profit, 1)} --- Current Price: {current_price_next}'
                                     f' --- Entry Price {current_price}')
                        if profit >= 1.8:
                            # Your position closing logic here
                            logging.info(f'Position closed successfully\n with Profit {profit}')
                            files_manager.insert_data(current_price, current_price_next, profit)
                            break
                        elif profit <= -0.569:
                            # Your position closing logic here
                            logging.info(f'Position closed successfully\n with Loss {profit}')
                            files_manager.insert_data(current_price, current_price_next, profit)
                            break

                # Place sell order if the price change is negative
                elif price_change_prediction < 0:
                    logging.info(f"Placing sell order at {current_price}")
                    # Your sell order logic here
                    while True:
                        current_price_next = float(client.futures_ticker(symbol=symbol)['lastPrice'])
                        profit = float(current_price) - float(current_price_next)
                        logging.info(f'Current profit/loss: {round(profit, 1)} --- Current Price: {current_price_next}'
                                     f' --- Entry Price {current_price}')
                        if profit >= 1.8:
                            # Your position closing logic here
                            logging.info(f'Position closed successfully\n with Profit {profit}')
                            files_manager.insert_data(current_price, current_price_next, profit)
                            break
                        elif profit <= -0.569:
                            # Your position closing logic here
                            logging.info(f'Position closed successfully\n with Loss {profit}')
                            files_manager.insert_data(current_price, current_price_next, profit)
                            break

            # Update X and y with the current trade's data for online learning
            X.append(features)
            y.append(price_change_prediction)
            train_model(X, y)  # Update the model with new data
            dump(model, model_filename)  # Save the model to disk

            time.sleep(20)  # Wait for 20 seconds before checking again

        # except Exception as e:
        #     print(f"An error occurred: {e}")



if __name__ == "__main__":
    range_trading_bot(symbol, interval, lookback_period, range_multiplier)
