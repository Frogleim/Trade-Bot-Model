import os
from dotenv import load_dotenv
import requests
import logging
import pandas as pd
from binance.client import Client

load_dotenv(dotenv_path='.env')
symbol = os.environ.get('SYMBOL')
interval = os.environ.get('INTERVAL')


def fetch_klines(symbol, interval):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching klines for {symbol}: {e}')
        return []



def get_last_price(symbol, interval='5m'):
    # API endpoint for Kline data
    url = "https://fapi.binance.com/fapi/v1/klines"

    # Parameters for the API request
    params = {
        "symbol": symbol,    # Trading pair symbol (e.g., BTCUSDT)
        "interval": interval, # Time interval (e.g., 1m, 5m, 1h)
        "limit": 1            # Number of candlesticks (set to 1 to get the latest one)
    }

    # Send the GET request
    response = requests.get(url, params=params)

    # Parse the response data
    if response.status_code == 200:
        klines = response.json()
        # The close price is the 5th element in the response for each kline
        last_candle = klines[0]  # Get the latest candle
        close_price = float(last_candle[4])  # The close price is at index 4
        return close_price
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

def fetch_btcusdt_klines(symbol, interval):
    result = fetch_klines(symbol, interval)

    # Process and store data for the symbol
    if result:
        df = pd.DataFrame(result, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        return df
    else:
        return pd.DataFrame()  # Return empty DataFrame if no data is fetched

def get_wallet():
    client = Client(api_key=os.environ['API_KEY'], api_secret=os.environ['API_SECRET'])
    futures_account = client.futures_account_balance()
    return futures_account[0]['availableBalance']





if __name__ == '__main__':
    fetch_btcusdt_klines('ADAUSDT', '5m')