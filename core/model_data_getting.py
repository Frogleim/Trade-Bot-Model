from binance.client import Client
import time
import config
import crypto_ticker
import files_manager
import logging
import os
import sys
from joblib import dump, load
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import numpy as np

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
model_path = f'./model/{model_filename}'

if os.path.exists(model_path):
    model = load(model_path)
else:
    model = DecisionTreeClassifier()

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


def collect_training_data(symbol, interval, lookback_period, buy_threshold, sell_threshold):
    klines = get_historical_data(symbol, interval, lookback_period)
    closes = [float(kline[4]) for kline in klines]
    signals = [1 if current_price < buy_threshold else -1 if current_price > sell_threshold else 0 for current_price in
               closes]
    return np.array(closes[:-1]), np.array(signals[1:])


# Function to train the model
def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = DecisionTreeClassifier()
    model.fit(X_train.reshape(-1, 1), y_train)
    y_pred = model.predict(X_test.reshape(-1, 1))
    accuracy = accuracy_score(y_test, y_pred)
    print(f'Model Accuracy: {accuracy}')
    return model


# Function to update the model with new data
def update_model(model, new_data):
    # Assume new_data is a single data point (closing price)
    prediction = model.predict(new_data.reshape(-1, 1))
    return prediction[0]


def calculate_sma(closes, window_size):
    return np.convolve(closes, np.ones(window_size)/window_size, mode='valid')


# Main trading function
# ... (your imports and API key initialization)

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

            # Get current price
            current_price = float(client.futures_ticker(symbol=symbol)['lastPrice'])

            # Set buy and sell thresholds
            buy_threshold = klines_range - (float(trading_range) * float(range_multiplier))
            sell_threshold = klines_range + (float(trading_range) * float(range_multiplier))
            closes, signals = collect_training_data(symbol, interval, lookback_period, buy_threshold, sell_threshold)
            model = train_model(closes, signals)
            signal = update_model(model, np.array([current_price]))

            logging.info(f'Current {config.trading_pair} price: {current_price} --- Buy Threshold: {buy_threshold}\n'
                         f'--- Sell threshold: {sell_threshold}')

            # Place buy order if the price is below the buy threshold
            if signal > 0:
                logging.info(f"Placing buy order at {current_price}")
                # crypto_ticker.place_buy_order(
                #     price=current_price,
                #     quantity=config.position_size,
                #     symbol=config.trading_pair
                # )
                while True:
                    current_price_next = float(client.futures_ticker(symbol=symbol)['lastPrice'])
                    (profit) = float(current_price_next) - float(current_price)
                    logging.info(f'Current profit/loss: {round(profit, 1)} --- Current Price: {current_price_next}'
                                 f' --- Entry Price {current_price}')
                    if profit >= 2.5:
                        # crypto_ticker.close_position(side='short', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Profit {profit}')
                        files_manager.insert_data(current_price, current_price_next, profit)
                        break

                    elif profit <= -config.SL:
                        logging.info(f'Current profit/loss: {round(profit)}')
                        # crypto_ticker.close_position(side='short', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Loss {profit}')
                        files_manager.insert_data(current_price, current_price_next, profit)
                        break

            elif signal < 0:
                # crypto_ticker.place_sell_order(
                #     price=current_price,
                #     quantity=config.position_size,
                #     symbol=config.trading_pair
                # )
                logging.info(f"Placing sell order at {current_price}")
                while True:
                    current_price_next = float(client.futures_ticker(symbol=symbol)['lastPrice'])
                    profit = float(current_price) - float(current_price_next)
                    logging.info(f'Current profit/loss: {round(profit, 1)} --- Current Price: {current_price_next}'
                                 f' --- Entry Price {current_price}')
                    if profit >= 2.5:
                        # crypto_ticker.close_position(side='long', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Profit {profit}')
                        files_manager.insert_data(current_price, current_price_next, profit)
                        break

                    elif profit <= -config.SL:
                        logging.info(f'Current profit/loss: {round(profit)}')
                        # crypto_ticker.close_position(side='long', quantity=config.position_size)
                        logging.info(f'Position closed successfully\n with Loss {profit}')
                        files_manager.insert_data(current_price, current_price_next, profit)
                        break

            time.sleep(45)  # Wait for 1 minute before checking again
            dump(model, model_path)  # Save the model to disk


        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    range_trading_bot(symbol, interval, lookback_period, range_multiplier)