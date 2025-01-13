import os
from dotenv import load_dotenv
import requests
import logging
import pandas as pd
from binance.client import Client
from concurrent.futures import ThreadPoolExecutor

load_dotenv(dotenv_path='../.env')
interval = os.environ.get('INTERVAL', '15m')
cryptos = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "ADAUSDT", "XRPUSDT"]  # List of five symbols

# Function to fetch klines for a specific symbol
def fetch_klines(symbol, interval):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching klines for {symbol}: {e}')
        return []

# Function to process klines for a specific symbol and return a DataFrame
def process_klines(symbol, interval):
    result = fetch_klines(symbol, interval)

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
        print(f"Data for {symbol}:")
        print(df.head())
        return df
    else:
        logging.warning(f"No data fetched for {symbol}")
        return pd.DataFrame()

# Function to fetch klines for multiple symbols concurrently
def fetch_multiple_klines(symbols, interval):
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_klines, symbol, interval): symbol for symbol in symbols}
        dataframes = {}
        for future in futures:
            symbol = futures[future]
            try:
                dataframes[symbol] = future.result()
            except Exception as e:
                logging.error(f"Error processing data for {symbol}: {e}")
        return dataframes

# Function to fetch the last price for a specific symbol
def get_last_price(symbol='BTCUSDT', interval='5m'):
    url = "https://fapi.binance.com/fapi/v1/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 1
    }
    response = requests.get(url, params=params, verify=False)
    if response.status_code == 200:
        klines = response.json()
        last_candle = klines[0]
        close_price = float(last_candle[4])
        print(f"Last price for {symbol}: {close_price}")
        return close_price
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

# Function to get wallet balance
def get_wallet():
    client = Client(api_key=os.environ['API_KEY'], api_secret=os.environ['API_SECRET'])
    futures_account = client.futures_account_balance()
    return futures_account[0]['availableBalance']

if __name__ == '__main__':
    print("Fetching data for multiple cryptocurrencies:")
    crypto_data = fetch_multiple_klines(cryptos, interval)

    for symbol, df in crypto_data.items():
        if not df.empty:
            print(f"{symbol} DataFrame size: {df.shape}")
        else:
            print(f"No data for {symbol}")
