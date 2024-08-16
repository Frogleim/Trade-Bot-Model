import warnings
import time
import pandas as pd
import numpy as np
from binance.client import Client
import aiohttp
import asyncio
import logging
import ta
from . import logging_settings
import ccxt.async_support as ccxt_async

warnings.filterwarnings(action='ignore')

api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

# Parameters
short_period = 5
long_period = 8
adx_period = 14
interval = Client.KLINE_INTERVAL_15MINUTE
start_str = '1 month ago UTC'
atr_period = 14

symbols = ['MATIC/USDT', 'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'ADA/USDT']

async def fetch_ohlcv(symbol, timeframe="15m", limit=1000):
    exchange = ccxt_async.binance()
    ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
    await exchange.close()
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df.set_index('timestamp', inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df

async def calculate_indicators(symbol):
    try:
        df = await fetch_ohlcv(symbol)
        
        df['close'] = df['close'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)

        if df.empty:
            logging_settings.error_logs_logger.error(f'DataFrame is empty after fetching data for {symbol}')
            return df

        # Calculate ADX
        df['ADX'] = ta.trend.adx(df['high'], df['low'], df['close'], window=adx_period)
        df['ATR'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'], window=atr_period)
        df['sar'] = ta.trend.PSARIndicator(high=df['high'], low=df['low'], close=df['close']).psar()
        
        # Calculate rolling highs and lows to identify support and resistance
        df['High_Rolling'] = df['high'].rolling(window=20).max()
        df['Low_Rolling'] = df['low'].rolling(window=20).min()

        df['Support'] = df['Low_Rolling'].shift(1)
        df['Resistance'] = df['High_Rolling'].shift(1)
        # Calculate EMAs
        df['EMA_Short'] = df['close'].ewm(span=short_period, adjust=False).mean()
        df['EMA_Long'] = df['close'].ewm(span=long_period, adjust=False).mean()

        df.dropna(inplace=True)

        if df.empty:
            logging_settings.error_logs_logger.error(f'DataFrame is empty after calculations for {symbol}')
        
        return df
    except Exception as e:
        logging_settings.error_logs_logger.error(f'Error in calculate_indicators for {symbol}: {e}')
        return pd.DataFrame()

async def check_signal(symbol):
    while True:
        data = await calculate_indicators(symbol)
        if data.empty:
            loggs.error_logs_logger.error(f'No data available during signal check for {symbol}')
            return symbol, 'No Data', None

        short_ema = data["EMA_Short"].iloc[-1]
        long_ema = data["EMA_Long"].iloc[-1]
        last_close_price = data['close'].iloc[-1]
        atr = data['ATR'].iloc[-1]
        adx = data['ADX'].iloc[-1]
        sar = data['sar'].iloc[-1]

        if short_ema > long_ema:
            if sar > short_ema and adx > 22:
                logging_settings.system_log.warning(f'{symbol} Sell signal detected.')
                return symbol, 'Sell', last_close_price
        elif short_ema < long_ema:
            if sar < short_ema and adx > 22:
                logging_settings.system_log.warning(f'{symbol} Buy signal detected.')
                return symbol, 'Buy', last_close_price
        else:
            logging_settings.system_log.warning(f'{symbol} No clear signal. Holding...')
            return symbol, 'Hold', last_close_price

        await asyncio.sleep(900)  # Wait for 15 minutes before the next check.
async def main():
    try:
        tasks = [check_signal(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks)
        for result in results:
            print(result)
    except Exception as e:
        logging_settings.error_logs_logger.error(f'EMA Crossover script down!\nError message: {e}')

if __name__ == '__main__':
    asyncio.run(main())
