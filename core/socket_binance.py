import requests
import logging
import pandas as pd

symbol = 'BTCUSDT'
interval = '5m'


def fetch_klines(symbol, interval):
    url = f'https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&interval={interval}'
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f'Error fetching klines for {symbol}: {e}')
        return []


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


if __name__ == '__main__':
    result_df = fetch_btcusdt_klines(symbol, interval)
    if not result_df.empty:
        print(f"Data for {symbol}:")
        print(result_df[['high', 'close', 'low']])
    else:
        print(f"No data available for {symbol}")
