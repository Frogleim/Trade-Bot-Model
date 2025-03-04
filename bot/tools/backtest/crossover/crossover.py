from binance.client import Client
import pandas as pd

client = Client(api_key='', api_secret='')


def fetch_btcusdt_klines(symbol, interval='1m', limit=1000):
    """Fetch BTCUSDT historical klines from Binance API."""
    klines = client.futures_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                       'close_time', 'quote_asset_volume', 'num_trades',
                                       'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    return df


def build_indicators(df):
    short_ema = df['close'].ewm(span=int(5), adjust=False).mean()
    long_ema = df['close'].ewm(span=int(10), adjust=False).mean()
    print(short_ema.iloc[-1], long_ema.iloc[-1])
    return short_ema, long_ema, df['close']


def live_test_signal():
    df = fetch_btcusdt_klines('SOLUSDT')
    short_ema, long_ema, close_price = build_indicators(df)
    entry_price = close_price.iloc[-1]
    if short_ema.iloc[-1] > long_ema.iloc[-1] and short_ema.iloc[-3] < long_ema.iloc[-3]:
        print(f'BUY SIGNAL {entry_price}')
    elif short_ema.iloc[-1] < long_ema.iloc[-1] and short_ema.iloc[-3] > long_ema.iloc[-3]:
        print(f'SELL SIGNAL {entry_price}')
    else:
        print('Hold signal')


def monitor_trade():
    pass

if __name__ == '__main__':

    import time

    while True:
        live_test_signal()
        time.sleep(20)