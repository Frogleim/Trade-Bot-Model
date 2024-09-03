from binance.client import Client
from ema_crossover import get_credentials
import pandas as pd

keys_data = get_credentials()
api_key = keys_data['api_key']
api_secret = keys_data['api_secret']
client = Client(api_key=api_key, api_secret=api_secret)
symbol = 'BTCUSDT'


def calculate_ema():
    data = client.futures_klines(symbol=symbol, interval='15m')
    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    short_ema = df['close'].ewm(span=5, adjust=False).mean()
    long_ema = df['close'].ewm(span=8, adjust=False).mean()
    close_price = df['close'].iloc[-2]
    return long_ema


def check_position(signal, entry_price):
    price_ticker = client.futures_ticker(symbol='BTCUSDT')
    last_price = price_ticker['lastPrice']
    long_ema = calculate_ema()
    print(f'Entry Price: {entry_price} ---> Target Price: {float(entry_price) + 80} ---> Long EMA: {long_ema.iloc[-1]}')
    if signal == 'Buy':
        if float(last_price) < float(long_ema.iloc[-1]):
            return 'Loss'
        if float(last_price) == float(entry_price) + 80:
            return 'Profit'
    elif signal == 'Sell':
        if float(last_price) > float(long_ema.iloc[-1]):
            return 'Loss'
        if float(last_price) == float(entry_price) - 80:
            return 'Profit'


if __name__ == '__main__':
    # while True:
    # time.sleep(1)
    check_position('Buy', 30000)
