import warnings

warnings.filterwarnings(action='ignore')

import pandas as pd
from binance.client import Client
import ta
from . import logging_settings

# Initialize the Binance client
api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'
client = Client(api_key, api_secret)
symbol = 'MATICUSDT'

short_period = 5
long_period = 8
adx_period = 14
atr_period = 14


# Function to fetch historical futures data
def fetch_futures_klines(symbol, interval, limit=500):
    klines =  client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df['close'] = df['close'].astype(float)
    return df


def get_df_15m():
    df_15m =  fetch_futures_klines(symbol, Client.KLINE_INTERVAL_15MINUTE)
    df_15m['SMA21'] = df_15m['close'].rolling(window=21).mean()
    return df_15m['SMA21'].iloc[-1]



def get_ema():
    try:
        df =  fetch_futures_klines(symbol, Client.KLINE_INTERVAL_15MINUTE)

        
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)

        if df.empty:
            logging_settings.error_logs_logger.error('DataFrame is empty after fetching data')
            return df

        # Calculate ADX
        df['ADX'] = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)
        df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=atr_period)


        # Calculate EMAs
        df['EMA_Short'] = df['close'].ewm(span=short_period, adjust=False).mean()
        df['EMA_Long'] = df['close'].ewm(span=long_period, adjust=False).mean()

        df.dropna(inplace=True)

        if df.empty:
            logging_settings.error_logs_logger.error('DataFrame is empty after calculations')
        
        return df['EMA_Long'].iloc[-1]
    except Exception as e:
        logging_settings.error_logs_logger.error(f'Error in calculate_indicators: {e}')
        return pd.DataFrame()


if __name__ == '__main__':
    long_ema = get_ema()
    print(long_ema)