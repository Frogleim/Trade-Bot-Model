from binance.client import Client
from ema_crossover import get_credentials
import pandas as pd
import logging_settings

keys_data = get_credentials()
api_key = keys_data['api_key']
api_secret = keys_data['api_secret']
client = Client(api_key=api_key, api_secret=api_secret)
symbol = 'BTCUSDT'


def calculate_ema():
    try:
        data = client.futures_klines(symbol=symbol, interval='15m')
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None, None

    df = pd.DataFrame(data, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    df['close'] = pd.to_numeric(df['close'])
    short_ema = df['close'].ewm(span=5, adjust=False).mean()
    long_ema = df['close'].ewm(span=8, adjust=False).mean()
    return short_ema, long_ema


def check_position(signal, entry_price):
    try:
        price_ticker = client.futures_ticker(symbol=symbol)
        last_price = float(price_ticker.get('lastPrice', 0))
    except Exception as e:
        logging_settings.system_log.info(f"Error fetching ticker data: {e}")
        return None
    short_ema, long_ema = calculate_ema()
    if long_ema is None:
        print("Failed to calculate EMA.")
        return None
    logging_settings.system_log.info(f'Entry Price: {entry_price} ---> Target Price: {entry_price + 80} ---> Long EMA: {long_ema.iloc[-1]}')
    if signal == 'Buy':
        if last_price < long_ema.iloc[-1]:
            return 'Loss'
        elif last_price >= entry_price + 80:
            print(
                f'Entry Price: {entry_price} ---> Target Price: {entry_price + 80} ---> Long EMA: {long_ema.iloc[-1]}')
            return 'Profit'
    elif signal == 'Sell':
        if last_price > long_ema.iloc[-1]:
            return 'Loss'
        elif last_price <= entry_price - 80:
            print(
                f'Entry Price: {entry_price} ---> Target Price: {entry_price + 80} ---> Long EMA: {long_ema.iloc[-1]}')

            return 'Profit'

    return 'No Action'


if __name__ == '__main__':
    # while True:
    # time.sleep(1)
    check_position('Buy', 30000)
